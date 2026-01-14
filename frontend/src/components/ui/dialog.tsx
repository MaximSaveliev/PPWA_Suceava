import * as React from "react"

interface DialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  children: React.ReactNode
}

interface DialogContentProps {
  children: React.ReactNode
  className?: string
}

interface DialogHeaderProps {
  children: React.ReactNode
  className?: string
}

interface DialogTitleProps {
  children: React.ReactNode
  className?: string
}

interface DialogDescriptionProps {
  children: React.ReactNode
  className?: string
}

interface DialogFooterProps {
  children: React.ReactNode
  className?: string
}

const Dialog = ({ open, onOpenChange, children }: DialogProps) => {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div 
        className="fixed inset-0 bg-black/50" 
        onClick={() => onOpenChange(false)}
      />
      <div className="relative bg-white rounded-lg shadow-lg max-w-lg w-full mx-4">
        {children}
      </div>
    </div>
  )
}

const DialogContent = ({ children, className = "" }: DialogContentProps) => {
  return <div className={className}>{children}</div>
}

const DialogHeader = ({ children, className = "" }: DialogHeaderProps) => {
  return <div className={`p-6 ${className}`}>{children}</div>
}

const DialogTitle = ({ children, className = "" }: DialogTitleProps) => {
  return <h2 className={`text-lg font-semibold ${className}`}>{children}</h2>
}

const DialogDescription = ({ children, className = "" }: DialogDescriptionProps) => {
  return <p className={`text-sm text-gray-500 mt-2 ${className}`}>{children}</p>
}

const DialogFooter = ({ children, className = "" }: DialogFooterProps) => {
  return <div className={`flex justify-end gap-2 p-6 pt-0 ${className}`}>{children}</div>
}

export { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter }
