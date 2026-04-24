export type ServiceCard = {
  id: string
  title: string
  type: "image" | "chart" | "options" | "text" | "table"
  desc?: string
  imageSrc?: string
  dataUrl?: string
  options?: string[]
  color: string
  border: string
}