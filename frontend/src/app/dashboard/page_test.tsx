'use client'

export default function DashboardTest() {
  return (
    <div className="min-h-screen bg-red-500">
      <div className="bg-yellow-500 text-black p-8 text-center font-bold text-2xl">
        🚨 TEST DASHBOARD - THIS SHOULD BE VISIBLE 🚨
      </div>
      <div className="bg-green-500 text-white p-4 text-center">
        If you see this, the file system is working correctly!
      </div>
    </div>
  )
}
