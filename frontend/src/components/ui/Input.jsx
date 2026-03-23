import { forwardRef } from 'react'

const Input = forwardRef(function Input({
  label,
  type = 'text',
  error,
  helperText,
  className = '',
  ...props
}, ref) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <input
        ref={ref}
        type={type}
        className={`
          w-full px-4 py-2 border rounded-lg transition-all
          focus:outline-none focus:ring-2 focus:ring-offset-0
          ${error
            ? 'border-red-500 focus:border-red-500 focus:ring-red-200'
            : 'border-gray-300 focus:border-primary-500 focus:ring-primary-200'
          }
          ${className}
        `}
        {...props}
      />
      {(error || helperText) && (
        <p className={`mt-1 text-sm ${error ? 'text-red-500' : 'text-gray-500'}`}>
          {error || helperText}
        </p>
      )}
    </div>
  )
})

export default Input