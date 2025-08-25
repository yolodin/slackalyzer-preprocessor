import React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import {
    BarChart3,
    Activity, Database, Home
} from 'lucide-react'

interface LayoutProps {
    children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    const router = useRouter()

    const navItems = [
        { href: '/', label: 'Overview', icon: Home },
        { href: '/processing', label: 'Processing', icon: Activity },
        { href: '/dashboard', label: 'Dashboard', icon: BarChart3 },
        { href: '/data', label: 'Data', icon: Database },
        // Disabled for MVP - focusing on core functionality
        // { href: '/ml-models', label: 'ML Models', icon: Brain },
        // { href: '/settings', label: 'Settings', icon: Settings },
    ]

    const isActive = (path: string) => {
        if (path === '/' && router.pathname === '/') return true
        if (path !== '/' && router.pathname.startsWith(path)) return true
        return false
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center">
                            <h1 className="text-xl font-semibold text-gray-900">
                                Hermes
                            </h1>
                            <span className="ml-2 px-2 py-1 text-xs font-medium bg-primary-100 text-primary-800 rounded-full">
                                MVP Dashboard
                            </span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                                <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                                <span className="text-sm text-gray-600">System Online</span>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            <div className="flex">
                {/* Sidebar */}
                <nav className="w-64 bg-white shadow-sm h-screen sticky top-0">
                    <div className="p-4">
                        <ul className="space-y-2">
                            {navItems.map((item) => {
                                const Icon = item.icon
                                return (
                                    <li key={item.href}>
                                        <Link
                                            href={item.href}
                                            className={`
                        flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-colors
                        ${isActive(item.href)
                                                    ? 'bg-primary-100 text-primary-700 border-r-2 border-primary-500'
                                                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                                                }
                      `}
                                        >
                                            <Icon className="mr-3 h-5 w-5" />
                                            {item.label}
                                        </Link>
                                    </li>
                                )
                            })}
                        </ul>
                    </div>
                </nav>

                {/* Main Content */}
                <main className="flex-1 p-8">
                    {children}
                </main>
            </div>
        </div>
    )
}

export default Layout 