import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Trash2 } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"

import { ItemsService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { DropdownMenuItem } from "@/components/ui/dropdown-menu"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
const logger = console;
import { handleError } from "@/utils"

interface DeleteItemProps {
  id: string
  onSuccess: () => void
}

const DeleteItem = ({ id, onSuccess }: DeleteItemProps) => {
logger.error('>>> Entering DeleteItem()', { "event.action": "DeleteItem" });
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { handleSubmit } = useForm()

logger.error(`DeleteItem(): queryClient → ${queryClient}`, { "event.action": "DeleteItem" });
logger.debug(`DeleteItem: isOpen → ${isOpen}`, { "event.action": "DeleteItem" });
  const deleteItem = async (id: string) => {
	logger.error(`>>> Entering deleteItem(id=${id})`, { "event.action": "deleteItem", "logrite.id": id });
    await ItemsService.deleteItem({ path: { id } })
	logger.warn('<<< Exiting DeleteItem()', { "event.action": "DeleteItem" });
	logger.warn(`<<< Exiting deleteItem(id=${id})`, { "event.action": "deleteItem", "logrite.id": id });
  }

  const mutation = useMutation({
    mutationFn: deleteItem,
    onSuccess: () => {
      showSuccessToast("The item was deleted successfully")
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries()
    },
  })

logger.error(`DeleteItem(): mutation.id → ${mutation?.id}`, { "event.action": "DeleteItem" });
  const onSubmit = async () => {
	logger.error('>>> Entering onSubmit()', { "event.action": "onSubmit" });
    mutation.mutate(id)
	logger.warn('<<< Exiting onSubmit()', { "event.action": "onSubmit" });
  }

logger.warn('<<< Exiting DeleteItem()', { "event.action": "DeleteItem" });
  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem
        variant="destructive"
        onSelect={(e) => e.preventDefault()}
        onClick={() => setIsOpen(true)}
      >
        <Trash2 />
        Delete Item
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Delete Item</DialogTitle>
            <DialogDescription>
              This item will be permanently deleted. Are you sure? You will not
              be able to undo this action.
            </DialogDescription>
          </DialogHeader>

          <DialogFooter className="mt-4">
            <DialogClose asChild>
              <Button variant="outline" disabled={mutation.isPending}>
                Cancel
              </Button>
            </DialogClose>
            <LoadingButton
              variant="destructive"
              type="submit"
              loading={mutation.isPending}
            >
              Delete
            </LoadingButton>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default DeleteItem
