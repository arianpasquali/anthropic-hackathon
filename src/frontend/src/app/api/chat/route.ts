import { Orq } from "@orq-ai/node"
import { NextRequest, NextResponse } from "next/server"

export const runtime = "nodejs"
export const dynamic = "force-dynamic"

const AGENT_KEY = "climate-harvest-assistant"

type ChatBody = {
  message: string
  task_id?: string
}

function getClient() {
  const apiKey = process.env.ORQ_API_KEY
  if (!apiKey) {
    throw new Error("ORQ_API_KEY missing — set it in .env.local")
  }
  return new Orq({ serverURL: "https://my.orq.ai", apiKey })
}

export async function POST(req: NextRequest) {
  let body: ChatBody
  try {
    body = (await req.json()) as ChatBody
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 })
  }

  const text = body.message?.trim()
  if (!text) {
    return NextResponse.json({ error: "Empty message" }, { status: 400 })
  }

  try {
    const client = getClient()
    const response = await client.agents.responses.create(
      {
        message: {
          role: "user",
          parts: [{ kind: "text", text }],
        },
        taskId: body.task_id,
      },
      AGENT_KEY,
    )

    // Narrow union — non-streaming response has `output`
    if (!("output" in response) || !Array.isArray(response.output)) {
      return NextResponse.json(
        { error: "Streaming response not supported in this route" },
        { status: 502 },
      )
    }

    const firstPart = response.output[0]?.parts?.[0]
    const reply =
      firstPart && "text" in firstPart && typeof firstPart.text === "string"
        ? firstPart.text
        : ""

    return NextResponse.json({
      reply,
      task_id: response.taskId,
      response_id: response.id,
      usage: response.usage ?? null,
    })
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error"
    console.error("[/api/chat] orq error:", message)
    return NextResponse.json(
      { error: "Assistant unavailable. Try again in a moment." },
      { status: 502 },
    )
  }
}
