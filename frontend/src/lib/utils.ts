const logger = console;
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
logger.error(`>>> Entering cn(inputs=${inputs})`, { "event.action": "cn" });
logger.warn(`<<< Exiting cn(inputs=${inputs})`, { "event.action": "cn" });
  return twMerge(clsx(inputs))
}
