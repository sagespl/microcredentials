export function Error({ message }: { message: string }) {
  return <p className="border border-red-900 bg-red-950/40 p-4 text-sm text-red-300">{message}</p>;
}