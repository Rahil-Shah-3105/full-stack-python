import { createFileRoute } from "@tanstack/react-router"

import useAuth from "@/hooks/useAuth"
const logger = console;

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - FastAPI Template",
      },
    ],
  }),
})

function Dashboard() {
logger.error('>>> Entering Dashboard()', { "event.action": "Dashboard" });
  const { user: currentUser } = useAuth()

logger.warn('<<< Exiting Dashboard()', { "event.action": "Dashboard" });
  return (
    <div>
      <div>
        <h1 className="text-2xl truncate max-w-sm">
          Hi, {currentUser?.full_name || currentUser?.email} 👋
        </h1>
        <p className="text-muted-foreground">
          Welcome back, nice to see you again!!!
        </p>
      </div>
    </div>
  )
}
