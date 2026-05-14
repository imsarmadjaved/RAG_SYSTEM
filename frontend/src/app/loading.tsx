export default function Loading() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
      <div className="text-center">
        <div className="relative w-16 h-16 mx-auto mb-6">
          <div className="absolute inset-0 border-4 border-blue-200 rounded-full" />
          <div className="absolute inset-0 border-4 border-transparent border-t-blue-600 rounded-full animate-spin" />
        </div>
        <p className="text-gray-500 text-sm animate-pulse">Loading...</p>
      </div>
    </div>
  );
}
