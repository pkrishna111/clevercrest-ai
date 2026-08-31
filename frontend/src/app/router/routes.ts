export const routePaths = {
  app: '/app',
  login: '/login',
  register: '/register',
  verifyEmail: '/verify-email',
  forgotPassword: '/forgot-password',
  resetPassword: '/reset-password',
} as const

// Placeholder scaffold for routes that are reserved but not yet implemented.
// /forgot-password and /reset-password have graduated to dedicated pages
// (ForgotPasswordPage / ResetPasswordPage) and are wired up explicitly in
// AppRouter, so they are no longer listed here.
export const publicRouteDefinitions: readonly { path: string; title: string }[] = []
