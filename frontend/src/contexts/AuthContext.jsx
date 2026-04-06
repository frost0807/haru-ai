import { createContext, useContext, useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { setUserId } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 현재 세션 확인 (페이지 새로고침 시)
    supabase.auth.getSession().then(({ data: { session } }) => {
      const u = session?.user ?? null
      setUser(u)
      setUserId(u?.id ?? null)
      setLoading(false)
    })

    // 로그인/로그아웃 이벤트 감지
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      const u = session?.user ?? null
      setUser(u)
      setUserId(u?.id ?? null)
    })

    return () => subscription.unsubscribe()
  }, [])

  const signInWithGoogle = () =>
    supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin + '/diary' },
    })

  const signOut = () => supabase.auth.signOut()

  return (
    <AuthContext.Provider value={{ user, loading, signInWithGoogle, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)