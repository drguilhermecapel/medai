interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_API_AUTH: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
