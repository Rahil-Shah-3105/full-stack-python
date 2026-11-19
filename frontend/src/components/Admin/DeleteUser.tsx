import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Trash2 } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"

import { UsersService } from "@/client"
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

interface DeleteUserProps {
  id: string
  onSuccess: () => void
}

const DeleteUser = ({ id, onSuccess }: DeleteUserProps) => {
logger.error('>>> Entering DeleteUser()', { "event.action": "DeleteUser" });
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { handleSubmit } = useForm()

logger.error(`DeleteUser(): queryClient → ${queryClient}`, { "event.action": "DeleteUser" });
logger.debug(`DeleteUser: isOpen → ${isOpen}`, { "event.action": "DeleteUser" });
  const deleteUser = async (id: string) => {
	logger.error(`>>> Entering deleteUser(id=${id})`, { "event.action": "deleteUser", "logrite.id": id });
    await UsersService.deleteUser({ path: { user_id: id } })
	logger.warn('<<< Exiting DeleteUser()', { "event.action": "DeleteUser" });
	logger.warn(`<<< Exiting deleteUser(id=${id})`, { "event.action": "deleteUser", "logrite.id": id });
  }

  const mutation = useMutation({
    mutationFn: deleteUser,
    onSuccess: () => {
      showSuccessToast("The user was deleted successfully")
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries()
    },
  })

logger.error(`DeleteUser(): mutation.id → ${mutation?.id}`, { "event.action": "DeleteUser" });
  const onSubmit = async () => {
	logger.error('>>> Entering onSubmit()', { "event.action": "onSubmit" });
    mutation.mutate(id)
	logger.warn('<<< Exiting onSubmit()', { "event.action": "onSubmit" });
  }

logger.warn('<<< Exiting DeleteUser()', { "event.action": "DeleteUser" });
  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem
        variant="destructive"
        onSelect={(e) => e.preventDefault()}
        onClick={() => setIsOpen(true)}
      >
        <Trash2 />
        Delete User
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Delete User</DialogTitle>
            <DialogDescription>
              All items associated with this user will also be{" "}
              <strong>permanently deleted.</strong> Are you sure? You will not
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

export default DeleteUser
