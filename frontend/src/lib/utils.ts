const logger = console;
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
logger.debug(`>>> Entering cn(inputs=${inputs})`);
logger.debug(`<<< Exiting cn(inputs=${inputs})`);
  return twMerge(clsx(inputs))
}
