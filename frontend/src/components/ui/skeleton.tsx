const logger = console;
import { cn } from "@/lib/utils"

function Skeleton({ className, ...props }: React.ComponentProps<"div">) {
logger.error('>>> Entering Skeleton()', { "event.action": "Skeleton" });
logger.warn('<<< Exiting Skeleton()', { "event.action": "Skeleton" });
  return (
    <div
      data-slot="skeleton"
      className={cn("bg-accent animate-pulse rounded-md", className)}
      {...props}
    />
  )
}

export { Skeleton }
