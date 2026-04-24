export default function GlassCard({
  title,
  children,
}: {
  title?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="glass rounded-2xl p-4">
      {title && <p className="text-sm text-gray-400 mb-2">{title}</p>}
      {children}
    </div>
  );
}
