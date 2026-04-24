'use client'
import { useEffect, useRef } from 'react'

type Star = {
  x: number
  y: number
  z: number
  color: string
}

export default function GalaxyField() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let width = (canvas.width = window.innerWidth)
    let height = (canvas.height = window.innerHeight)

    const centerX = () => width / 2
    const centerY = () => height / 2

    const galaxyColors: string[] = [
      'rgba(120,180,255,',
      'rgba(180,120,255,',
      'rgba(255,120,180,',
      'rgba(255,200,120,',
    ]

    const STAR_COUNT = 900
    const DEPTH = 2000

    function createStar(): Star {
      return {
        x: (Math.random() - 0.5) * width,
        y: (Math.random() - 0.5) * height,
        z: Math.random() * DEPTH + 1, // 🔑 avoid z = 0
        color: galaxyColors[Math.floor(Math.random() * galaxyColors.length)],
      }
    }

    const stars: Star[] = Array.from({ length: STAR_COUNT }, createStar)

    let mouseX = 0
    let mouseY = 0

    const onMouseMove = (e: MouseEvent) => {
      mouseX = (e.clientX - centerX()) * 0.0005
      mouseY = (e.clientY - centerY()) * 0.0005
    }

    const onResize = () => {
      width = canvas.width = window.innerWidth
      height = canvas.height = window.innerHeight
    }

    window.addEventListener('mousemove', onMouseMove)
    window.addEventListener('resize', onResize)

    const animate = () => {
      ctx.clearRect(0, 0, width, height)
      ctx.fillStyle = '#000'
      ctx.fillRect(0, 0, width, height)

      for (const star of stars) {
        star.z -= 6

        if (star.z <= 1) {
          Object.assign(star, createStar(), { z: DEPTH })
        }

        const scale = 600 / star.z
        const x = star.x * scale + centerX()
        const y = star.y * scale + centerY()

        const radius = Math.max(0.5, scale * 1.2)
        const alpha = Math.min(1, scale * 2)

        ctx.beginPath()
        ctx.fillStyle = `${star.color}${alpha})`
        ctx.arc(
          x + mouseX * star.z,
          y + mouseY * star.z,
          radius,
          0,
          Math.PI * 2
        )
        ctx.fill()
      }

      requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('mousemove', onMouseMove)
      window.removeEventListener('resize', onResize)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 0 }}
    />
  )
}
