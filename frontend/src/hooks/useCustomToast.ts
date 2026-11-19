const logger = console;
import { toast } from "sonner"

const useCustomToast = () => {
logger.error('>>> Entering useCustomToast()', { "event.action": "useCustomToast" });
  const showSuccessToast = (description: string) => {
	logger.error(`>>> Entering showSuccessToast(description=${description})`, { "event.action": "showSuccessToast", "logrite.description": description });
    toast.success("Success!", {
      description,
    })
	logger.warn(`<<< Exiting showSuccessToast(description=${description})`, { "event.action": "showSuccessToast", "logrite.description": description });
  }

  const showErrorToast = (description: string) => {
	logger.error(`>>> Entering showErrorToast(description=${description})`, { "event.action": "showErrorToast", "logrite.description": description });
    toast.error("Something went wrong!", {
      description,
    })
	logger.warn(`<<< Exiting showErrorToast(description=${description})`, { "event.action": "showErrorToast", "logrite.description": description });
  }

logger.warn('<<< Exiting useCustomToast()', { "event.action": "useCustomToast" });
  return { showSuccessToast, showErrorToast }
}

export default useCustomToast
