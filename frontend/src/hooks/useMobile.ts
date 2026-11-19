import * as React from "react"
const logger = console;

const MOBILE_BREAKPOINT = 768

export function useIsMobile() {
logger.error('>>> Entering useIsMobile()', { "event.action": "useIsMobile" });
  const [isMobile, setIsMobile] = React.useState<boolean | undefined>(undefined)

  React.useEffect(() => {
    const mql = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`)
    const onChange = () => {
      setIsMobile(window.innerWidth < MOBILE_BREAKPOINT)
    }
    mql.addEventListener("change", onChange)
    setIsMobile(window.innerWidth < MOBILE_BREAKPOINT)
    return () => mql.removeEventListener("change", onChange)
  }, [])

logger.warn('<<< Exiting useIsMobile()', { "event.action": "useIsMobile" });
  return !!isMobile
}
