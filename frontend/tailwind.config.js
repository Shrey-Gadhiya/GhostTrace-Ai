/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#FAF7F7",
        surface: "#FFFFFF",
        rosegold: {
          50: "#FDF8F9",
          100: "#FAF0F2",
          200: "#F4DEE2",
          300: "#EAC5CB",
          400: "#D89FA7",
          500: "#B76E79", // Canonical metallic rose gold
          600: "#A25964",
          700: "#89434E",
          800: "#70353F",
          900: "#4D2128",
          950: "#2B1116",
        },
        noir: {
          950: "#140B0D",
          900: "#1C1114",
          850: "#24171A",
          800: "#2D1D21",
          700: "#422B31",
          600: "#5A3C44",
        },
        primary: {
          DEFAULT: "#B76E79",
          hover: "#A25964",
          dark: "#89434E",
          light: "#FAF0F2"
        },
        slate: {
          50: "#FAFAFA",
          100: "#F5F3F4",
          200: "#EAE7E8",
          300: "#D7D2D4",
          400: "#A8A2A5",
          500: "#787175",
          600: "#554E52",
          700: "#3D363A",
          800: "#282226",
          900: "#1C1619",
        },
        status: {
          complete: {
            bg: "#F2FAF6",
            border: "#C2ECD8",
            text: "#0D6847"
          },
          incomplete: {
            bg: "#FDF3F4",
            border: "#F5CAD0",
            text: "#A82A3A"
          },
          na: {
            bg: "#F8F6F6",
            border: "#E2DCDD",
            text: "#635B5E"
          },
          warning: {
            bg: "#FDF8F0",
            border: "#F7E2BF",
            text: "#9A5D15"
          }
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace']
      }
    },
  },
  plugins: [],
}
