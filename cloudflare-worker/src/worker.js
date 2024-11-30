/**
 * Welcome to Cloudflare Workers! This is your worker with extended functionality.
 *
 * - Run "npm run dev" in your terminal to start a development server
 * - Open a browser tab at http://localhost:8787/ to see your worker in action
 * - Run "npm run deploy" to publish your worker
 *
 * Learn more at https://developers.cloudflare.com/workers/
 */

export default {
  async fetch(request, env, ctx) {
    // Parse the incoming request URL
    const url = new URL(request.url);

    // Tester endpoint to confirm Worker is running
    if (url.pathname === "/test" && request.method === "GET") {
      return new Response("Cloudflare Worker is running!", { status: 200 });
    }

    // Endpoint to fetch the latest code from VS Code extension
    if (url.pathname === "/getCode" && request.method === "GET") {
      try {
        // Fetch code from the local VS Code extension server
        const response = await fetch("http://localhost:3000/getCode");
        if (!response.ok) {
          return new Response("Failed to fetch code from VS Code extension", { status: 500 });
        }
        const code = await response.text();
        return new Response(JSON.stringify({ code }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      } catch (error) {
        return new Response(`Error fetching code: ${error.message}`, { status: 500 });
      }
    }

    // Endpoint to process query and code with GPT-4 (via Voiceflow API)
    if (url.pathname === "/processQuery" && request.method === "POST") {
      try {
        // Parse the JSON body from the incoming request
        const { query, code } = await request.json();

        // Forward the query and code to GPT-4 via Voiceflow's API
        const response = await fetch("https://api.voiceflow.com/gpt4/process", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer YOUR_VOICEFLOW_API_KEY", // Replace with your Voiceflow API key
          },
          body: JSON.stringify({ query, code }),
        });

        if (!response.ok) {
          return new Response("Failed to process query with Voiceflow", { status: 500 });
        }

        const suggestions = await response.json();
        return new Response(JSON.stringify(suggestions), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      } catch (error) {
        return new Response(`Error processing query: ${error.message}`, { status: 500 });
      }
    }

    // Default response for undefined routes
    return new Response("Not Found", { status: 404 });
  },
};
