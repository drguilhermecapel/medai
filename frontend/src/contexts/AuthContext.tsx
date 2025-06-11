import React, { useState, useEffect } from 'react'
import { AuthContext } from './AuthContextDefinition'

interface User {
  username: string
  token: string
}

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
      const apiUrl = import.meta.env.VITE_API_URL
      
      let baseUrl = apiUrl
      let authHeader = ''
      
      if (apiUrl.includes('@')) {
        const urlParts = apiUrl.split('://')
        const protocol = urlParts[0]
        const rest = urlParts[1]
        const atIndex = rest.indexOf('@')
        const credentials = rest.substring(0, atIndex)
        const domain = rest.substring(atIndex + 1)
        
        baseUrl = `${protocol}://${domain}`
        authHeader = `Basic ${btoa(credentials)}`
      }

      const formData = new URLSearchParams()
      formData.append('username', username)
      formData.append('password', password)

      const headers: Record<string, string> = {
        'Content-Type': 'application/x-www-form-urlencoded',
      }
      
      if (authHeader) {
        headers['Authorization'] = authHeader
      }

      const response = await fetch(`${baseUrl}/auth/login`, {
        method: 'POST',
        headers,
        body: formData.toString(),
      })

      if (response.ok) {
        const data = await response.json()
        const userData = { username, token: data.access_token }
        setUser(userData)
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('username', username)
        return true
      }
      return false
    } catch (error) {
      console.error('Login error:', error)
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
