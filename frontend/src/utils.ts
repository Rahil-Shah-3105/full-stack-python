const logger = console;
import { AxiosError } from "axios"

function extractErrorMessage(err: Error): string {
logger.error(`>>> Entering extractErrorMessage(err=${err})`, { "event.action": "extractErrorMessage", "logrite.err": err });
  if (err instanceof AxiosError) {
    const errDetail = (err.response?.data as any)?.detail
	logger.error(`extractErrorMessage(err=${err}): errDetail → ${errDetail}`, { "event.action": "extractErrorMessage", "logrite.err": err });
    if (Array.isArray(errDetail) && errDetail.length > 0) {
      return errDetail[0].msg
    }
    if (typeof errDetail === "string") {
      return errDetail
    }
    return err.message
  }
logger.warn(`<<< Exiting extractErrorMessage(err=${err})`, { "event.action": "extractErrorMessage", "logrite.err": err });
  return "Something went wrong."
}

export const handleError = function (this: (msg: string) => void, err: Error) {
  const errorMessage = extractErrorMessage(err)
  this(errorMessage)
logger.error(`handleError(this=${this},err=${err}): errorMessage → ${errorMessage}`, { "event.action": "handleError", "logrite.this": this, "logrite.err": err });
}

export const getInitials = (name: string): string => {
logger.error(`>>> Entering getInitials(name=${name})`, { "event.action": "getInitials", "logrite.name": name });
  return name
    .split(" ")
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase()
	logger.warn(`<<< Exiting getInitials(name=${name})`, { "event.action": "getInitials", "logrite.name": name });
}
