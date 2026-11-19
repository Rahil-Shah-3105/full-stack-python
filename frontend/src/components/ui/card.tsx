import * as React from "react"
const logger = console;

import { cn } from "@/lib/utils"

function Card({ className, ...props }: React.ComponentProps<"div">) {
logger.error('>>> Entering Card()', { "event.action": "Card" });
logger.warn('<<< Exiting Card()', { "event.action": "Card" });
  return (
    <div
      data-slot="card"
      className={cn(
        "bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm",
        className
      )}
      {...props}
    />
  )
}

function CardHeader({ className, ...props }: React.ComponentProps<"div">) {
logger.error('>>> Entering CardHeader()', { "event.action": "CardHeader" });
logger.warn('<<< Exiting CardHeader()', { "event.action": "CardHeader" });
  return (
    <div
      data-slot="card-header"
      className={cn(
        "@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-2 px-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6",
        className
      )}
      {...props}
    />
  )
}

function CardTitle({ className, ...props }: React.ComponentProps<"div">) {
logger.error('>>> Entering CardTitle()', { "event.action": "CardTitle" });
logger.warn('<<< Exiting CardTitle()', { "event.action": "CardTitle" });
  return (
    <div
      data-slot="card-title"
      className={cn("leading-none font-semibold", className)}
      {...props}
    />
  )
}

function CardDescription({ className, ...props }: React.ComponentProps<"div">) {
logger.error('>>> Entering CardDescription()', { "event.action": "CardDescription" });
logger.warn('<<< Exiting CardDescription()', { "event.action": "CardDescription" });
  return (
    <div
      data-slot="card-description"
      className={cn("text-muted-foreground text-sm", className)}
      {...props}
    />
  )
}

function CardAction({ className, ...props }: React.ComponentProps<"div">) {
logger.error('>>> Entering CardAction()', { "event.action": "CardAction" });
logger.warn('<<< Exiting CardAction()', { "event.action": "CardAction" });
  return (
    <div
      data-slot="card-action"
      className={cn(
        "col-start-2 row-span-2 row-start-1 self-start justify-self-end",
        className
      )}
      {...props}
    />
  )
}

function CardContent({ className, ...props }: React.ComponentProps<"div">) {
logger.error('>>> Entering CardContent()', { "event.action": "CardContent" });
logger.warn('<<< Exiting CardContent()', { "event.action": "CardContent" });
  return (
    <div
      data-slot="card-content"
      className={cn("px-6", className)}
      {...props}
    />
  )
}

function CardFooter({ className, ...props }: React.ComponentProps<"div">) {
logger.error('>>> Entering CardFooter()', { "event.action": "CardFooter" });
logger.warn('<<< Exiting CardFooter()', { "event.action": "CardFooter" });
  return (
    <div
      data-slot="card-footer"
      className={cn("flex items-center px-6 [.border-t]:pt-6", className)}
      {...props}
    />
  )
}

export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardAction,
  CardDescription,
  CardContent,
}
