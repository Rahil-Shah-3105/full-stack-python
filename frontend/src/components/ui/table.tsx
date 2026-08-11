import * as React from "react"
const logger = console;

import { cn } from "@/lib/utils"

function Table({ className, ...props }: React.ComponentProps<"table">) {
logger.debug(`>>> Entering Table(className=${className},props=${props})`);
logger.debug(`<<< Exiting Table(className=${className},props=${props})`);
  return (
    <div
      data-slot="table-container"
      className="relative w-full overflow-x-auto rounded-lg border"
    >
      <table
        data-slot="table"
        className={cn("w-full caption-bottom text-sm", className)}
        {...props}
      />
    </div>
  )
}

function TableHeader({ className, ...props }: React.ComponentProps<"thead">) {
logger.debug(`>>> Entering TableHeader(className=${className},props=${props})`);
logger.debug(`<<< Exiting TableHeader(className=${className},props=${props})`);
  return (
    <thead
      data-slot="table-header"
      className={cn("bg-muted/50 [&_tr]:border-b", className)}
      {...props}
    />
  )
}

function TableBody({ className, ...props }: React.ComponentProps<"tbody">) {
logger.debug(`>>> Entering TableBody(className=${className},props=${props})`);
logger.debug(`<<< Exiting TableBody(className=${className},props=${props})`);
  return (
    <tbody
      data-slot="table-body"
      className={cn("[&_tr:last-child]:border-0", className)}
      {...props}
    />
  )
}

function TableFooter({ className, ...props }: React.ComponentProps<"tfoot">) {
logger.debug(`>>> Entering TableFooter(className=${className},props=${props})`);
logger.debug(`<<< Exiting TableFooter(className=${className},props=${props})`);
  return (
    <tfoot
      data-slot="table-footer"
      className={cn(
        "bg-muted/50 border-t font-medium [&>tr]:last:border-b-0",
        className
      )}
      {...props}
    />
  )
}

function TableRow({ className, ...props }: React.ComponentProps<"tr">) {
logger.debug(`>>> Entering TableRow(className=${className},props=${props})`);
logger.debug(`<<< Exiting TableRow(className=${className},props=${props})`);
  return (
    <tr
      data-slot="table-row"
      className={cn(
        "hover:bg-muted/50 data-[state=selected]:bg-muted border-b transition-colors",
        className
      )}
      {...props}
    />
  )
}

function TableHead({ className, ...props }: React.ComponentProps<"th">) {
logger.debug(`>>> Entering TableHead(className=${className},props=${props})`);
logger.debug(`<<< Exiting TableHead(className=${className},props=${props})`);
  return (
    <th
      data-slot="table-head"
      className={cn(
        "text-muted-foreground h-11 px-4 text-left align-middle text-xs font-semibold uppercase tracking-wider whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]",
        className
      )}
      {...props}
    />
  )
}

function TableCell({ className, ...props }: React.ComponentProps<"td">) {
logger.debug(`>>> Entering TableCell(className=${className},props=${props})`);
logger.debug(`<<< Exiting TableCell(className=${className},props=${props})`);
  return (
    <td
      data-slot="table-cell"
      className={cn(
        "px-4 py-3 align-middle whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]",
        className
      )}
      {...props}
    />
  )
}

function TableCaption({
  className,
  ...props
}: React.ComponentProps<"caption">) {
  return (
    <caption
      data-slot="table-caption"
      className={cn("text-muted-foreground mt-4 text-sm", className)}
      {...props}
    />
  )
}

export {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableHead,
  TableRow,
  TableCell,
  TableCaption,
}
