import httpx
import asyncio
import pandas as pd

class NOAAFetcher:
    """
    Handles lightweight data fetching from NOAA SWPC (Space Weather Prediction Center).
    """
    
    GOES_URL_PRIMARY = "https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json"
    GOES_URL_SECONDARY = "https://services.swpc.noaa.gov/json/goes/secondary/xrays-6-hour.json"

    @staticmethod
    def _process(response) -> list:
        """
        Cleans raw GOES JSON into a list of { time_tag, flux } dicts.
        Returns empty list if fetch failed.
        """
        if isinstance(response, Exception):
            print(f"GOES fetch failed: {response}")
            return []
        
        df = pd.DataFrame(response.json())
        
        long_flux = df[
            (df['energy'] == '0.1-0.8nm') &
            (df['observed_flux'] > 0)
        ].copy()

        return long_flux[['time_tag', 'flux']].tail(200).to_dict(orient='records')

    @staticmethod
    async def get_goes_xray_flux():
        """
        Fetches GOES-16 (primary) and GOES-17 (secondary) simultaneously.
        Returns both separately for dual-plot in frontend.
        """
        async with httpx.AsyncClient() as client:
            primary_res, secondary_res = await asyncio.gather(
                client.get(NOAAFetcher.GOES_URL_PRIMARY, timeout=5.0),
                client.get(NOAAFetcher.GOES_URL_SECONDARY, timeout=5.0),
                return_exceptions=True  # don't crash if one fails
            )

        return {
            "primary": NOAAFetcher._process(primary_res),    # GOES-16
            "secondary": NOAAFetcher._process(secondary_res) # GOES-17/18
        }