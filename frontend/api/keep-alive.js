export default async function handler(req, res) {
    try {
        const backendUrl =
            process.env.VITE_API_URL || "https://nyayaai-backend.onrender.com";
        const response = await fetch(`${backendUrl}/health`, {
            method: "GET",
            headers: { Accept: "application/json" },
        });
        const data = await response.json();
        res.status(200).json({
            status: "ok",
            timestamp: new Date().toISOString(),
            backend: data,
        });
    } catch (error) {
        res.status(500).json({
            status: "error",
            timestamp: new Date().toISOString(),
            message: error.message,
        });
    }
}
