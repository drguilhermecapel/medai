import React, { useState, useEffect } from 'react'
import { AuthContext } from './AuthContextDefinition'

interface User {
  username: string
  token: string
}

const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? ''

const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }): JSX.Element => {
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const username = localStorage.getItem('username')
    if (token && username) {
      setUser({ username, token })
    }
  }, [])

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const formData = new URLSearchParams()
      formData.append('username', username)
      formData.append('password', password)

      const response = await fetch(`${API_BASE}/api/v1/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      })

      if (!response.ok) {
        return false
      }

      const data = await response.json()
      setUser({ username, token: data.access_token })
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('username', username)
      return true
    } catch {
      return false
    }
  }

  const logout = (): void => {
    setUser(null)
    localStorage.removeItem('token')
    localStorage.removeItem('username')
  }

  const value = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export { AuthProvider }
