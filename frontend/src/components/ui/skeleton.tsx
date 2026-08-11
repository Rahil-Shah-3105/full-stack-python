const logger = console;
import { cn } from "@/lib/utils"

function Skeleton({ className, ...props }: React.ComponentProps<"div">) {
logger.debug(`>>> Entering Skeleton(className=${className},props=${props})`);
logger.debug(`<<< Exiting Skeleton(className=${className},props=${props})`);
  return (
    <div
      data-slot="skeleton"
      className={cn("bg-accent animate-pulse rounded-md", className)}
      {...props}
    />
  )
}

export { Skeleton }
