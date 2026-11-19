import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { ItemPublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteItem from "../Items/DeleteItem"
import EditItem from "../Items/EditItem"
const logger = console;

interface ItemActionsMenuProps {
  item: ItemPublic
}

export const ItemActionsMenu = ({ item }: ItemActionsMenuProps) => {
logger.error('>>> Entering ItemActionsMenu()', { "event.action": "ItemActionsMenu" });
  const [open, setOpen] = useState(false)

logger.warn('<<< Exiting ItemActionsMenu()', { "event.action": "ItemActionsMenu" });
  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditItem item={item} onSuccess={() => setOpen(false)} />
        <DeleteItem id={item.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
