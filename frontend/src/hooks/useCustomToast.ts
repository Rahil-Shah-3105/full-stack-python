const logger = console;
import { toast } from "sonner"

const useCustomToast = () => {
logger.debug('>>> Entering useCustomToast()');
  const showSuccessToast = (description: string) => {
	logger.debug(`>>> Entering showSuccessToast(description=${description})`);
    toast.success("Success!", {
      description,
    })
  }
	logger.debug(`<<< Exiting showSuccessToast(description=${description})`);

  const showErrorToast = (description: string) => {
	logger.debug(`>>> Entering showErrorToast(description=${description})`);
    toast.error("Something went wrong!", {
      description,
    })
  }
	logger.debug(`<<< Exiting showErrorToast(description=${description})`);

logger.debug('<<< Exiting useCustomToast()');
  return { showSuccessToast, showErrorToast }
}

export default useCustomToast
