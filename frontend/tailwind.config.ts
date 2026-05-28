import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#04070f",
          900: "#08101d",
          800: "#0e1729"
        }
      },
      boxShadow: {
        glass: "0 0 0 1px rgba(255,255,255,0.08), 0 24px 80px rgba(0,0,0,0.35)"
      },
      backgroundImage: {
        mesh:
          "radial-gradient(circle at 20% 20%, rgba(56,189,248,0.12), transparent 30%), radial-gradient(circle at 80% 10%, rgba(168,85,247,0.12), transparent 25%), radial-gradient(circle at 70% 80%, rgba(34,197,94,0.10), transparent 25%)"
      }
    }
  },
  plugins: []
};

export default config;

