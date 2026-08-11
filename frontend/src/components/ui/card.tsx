import * as React from "react"
const logger = console;

import { cn } from "@/lib/utils"

function Card({ className, ...props }: React.ComponentProps<"div">) {
logger.debug(`>>> Entering Card(className=${className},props=${props})`);
logger.debug(`<<< Exiting Card(className=${className},props=${props})`);
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
logger.debug(`>>> Entering CardHeader(className=${className},props=${props})`);
logger.debug(`<<< Exiting CardHeader(className=${className},props=${props})`);
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
logger.debug(`>>> Entering CardTitle(className=${className},props=${props})`);
logger.debug(`<<< Exiting CardTitle(className=${className},props=${props})`);
  return (
    <div
      data-slot="card-title"
      className={cn("leading-none font-semibold", className)}
      {...props}
    />
  )
}

function CardDescription({ className, ...props }: React.ComponentProps<"div">) {
logger.debug(`>>> Entering CardDescription(className=${className},props=${props})`);
logger.debug(`<<< Exiting CardDescription(className=${className},props=${props})`);
  return (
    <div
      data-slot="card-description"
      className={cn("text-muted-foreground text-sm", className)}
      {...props}
    />
  )
}

function CardAction({ className, ...props }: React.ComponentProps<"div">) {
logger.debug(`>>> Entering CardAction(className=${className},props=${props})`);
logger.debug(`<<< Exiting CardAction(className=${className},props=${props})`);
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
logger.debug(`>>> Entering CardContent(className=${className},props=${props})`);
logger.debug(`<<< Exiting CardContent(className=${className},props=${props})`);
  return (
    <div
      data-slot="card-content"
      className={cn("px-6", className)}
      {...props}
    />
  )
}

function CardFooter({ className, ...props }: React.ComponentProps<"div">) {
logger.debug(`>>> Entering CardFooter(className=${className},props=${props})`);
logger.debug(`<<< Exiting CardFooter(className=${className},props=${props})`);
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
