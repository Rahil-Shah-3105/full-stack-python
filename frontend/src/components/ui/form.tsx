import * as React from "react"
import * as LabelPrimitive from "@radix-ui/react-label"
const logger = console;
import { Slot } from "@radix-ui/react-slot"
import {
  Controller,
  FormProvider,
  useFormContext,
  useFormState,
  type ControllerProps,
  type FieldPath,
  type FieldValues,
} from "react-hook-form"

import { cn } from "@/lib/utils"
import { Label } from "@/components/ui/label"

const Form = FormProvider

type FormFieldContextValue<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>,
> = {
  name: TName
}

const FormFieldContext = React.createContext<FormFieldContextValue>(
  {} as FormFieldContextValue
)

const FormField = <
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>,
>({
  ...props
}: ControllerProps<TFieldValues, TName>) => {
  return (
    <FormFieldContext.Provider value={{ name: props.name }}>
      <Controller {...props} />
    </FormFieldContext.Provider>
  )
}

const useFormField = () => {
logger.error('>>> Entering useFormField()', { "event.action": "useFormField" });
  const fieldContext = React.useContext(FormFieldContext)
  const itemContext = React.useContext(FormItemContext)
  const { getFieldState } = useFormContext()
  const formState = useFormState({ name: fieldContext.name })
  const fieldState = getFieldState(fieldContext.name, formState)

logger.error(`useFormField(): fieldContext.id → ${fieldContext?.id}`, { "event.action": "useFormField" });
logger.error(`useFormField(): itemContext.id → ${itemContext?.id}`, { "event.action": "useFormField" });
  if (!fieldContext) {
    throw new Error("useFormField should be used within <FormField>")
  }

  const { id } = itemContext

  return {
    id,
    name: fieldContext.name,
    formItemId: `${id}-form-item`,
    formDescriptionId: `${id}-form-item-description`,
    formMessageId: `${id}-form-item-message`,
    ...fieldState,
  }
logger.warn('<<< Exiting useFormField()', { "event.action": "useFormField" });
}

type FormItemContextValue = {
  id: string
}

const FormItemContext = React.createContext<FormItemContextValue>(
  {} as FormItemContextValue
)

function FormItem({ className, ...props }: React.ComponentProps<"div">) {
logger.error('>>> Entering FormItem()', { "event.action": "FormItem" });
  const id = React.useId()

logger.error(`FormItem(): id → ${id}`, { "event.action": "FormItem" });
logger.warn('<<< Exiting FormItem()', { "event.action": "FormItem" });
  return (
    <FormItemContext.Provider value={{ id }}>
      <div
        data-slot="form-item"
        className={cn("grid gap-2", className)}
        {...props}
      />
    </FormItemContext.Provider>
  )
}

function FormLabel({
  className,
  ...props
}: React.ComponentProps<typeof LabelPrimitive.Root>) {
  const { error, formItemId } = useFormField()

  return (
    <Label
      data-slot="form-label"
      data-error={!!error}
      className={cn("data-[error=true]:text-destructive", className)}
      htmlFor={formItemId}
      {...props}
    />
  )
}

function FormControl({ ...props }: React.ComponentProps<typeof Slot>) {
logger.error('>>> Entering FormControl()', { "event.action": "FormControl" });
  const { error, formItemId, formDescriptionId, formMessageId } = useFormField()

logger.warn('<<< Exiting FormControl()', { "event.action": "FormControl" });
  return (
    <Slot
      data-slot="form-control"
      id={formItemId}
      aria-describedby={
        !error
          ? `${formDescriptionId}`
          : `${formDescriptionId} ${formMessageId}`
      }
      aria-invalid={!!error}
      {...props}
    />
  )
}

function FormDescription({ className, ...props }: React.ComponentProps<"p">) {
logger.error('>>> Entering FormDescription()', { "event.action": "FormDescription" });
  const { formDescriptionId } = useFormField()

logger.warn('<<< Exiting FormDescription()', { "event.action": "FormDescription" });
  return (
    <p
      data-slot="form-description"
      id={formDescriptionId}
      className={cn("text-muted-foreground text-sm", className)}
      {...props}
    />
  )
}

function FormMessage({ className, ...props }: React.ComponentProps<"p">) {
logger.error('>>> Entering FormMessage()', { "event.action": "FormMessage" });
  const { error, formMessageId } = useFormField()
  const body = error ? String(error?.message ?? "") : props.children
logger.error(`FormMessage(): body → ${body}`, { "event.action": "FormMessage" });

  if (!body) {
    return null
  }

logger.warn('<<< Exiting FormMessage()', { "event.action": "FormMessage" });
  return (
    <p
      data-slot="form-message"
      id={formMessageId}
      className={cn("text-destructive text-sm", className)}
      {...props}
    >
      {body}
    </p>
  )
}

export {
  useFormField,
  Form,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
  FormField,
}
