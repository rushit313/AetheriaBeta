import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Client-Info, Apikey",
};

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 200,
      headers: corsHeaders,
    });
  }

  try {
    const { renderImage, referenceImage } = await req.json();

    if (!renderImage) {
      return new Response(
        JSON.stringify({ error: 'Render image is required' }),
        {
          status: 400,
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
          },
        }
      );
    }

    const systemPrompt = `You are an expert 3D rendering professional with years of experience in computer graphics, visual effects, and digital art. Your role is to provide constructive, detailed feedback on 3D renders to help artists improve their work.

When analyzing renders, focus on:
1. Lighting - Quality, realism, mood, shadows, highlights, color temperature
2. Materials & Textures - Surface properties, realism, detail, UV mapping quality
3. Composition - Framing, focal points, rule of thirds, visual balance
4. Technical Quality - Resolution, noise/grain, artifacts, render settings
5. Artistic Direction - Mood, storytelling, atmosphere, color palette
6. Realism vs Stylization - Appropriateness for the intended style

Provide specific, actionable feedback. Be encouraging but honest. Structure your feedback with clear sections.`;

    let userPrompt = 'Please analyze this 3D render and provide detailed feedback on how to improve it.';
    
    if (referenceImage) {
      userPrompt += '\n\nA reference image has been provided. Please compare the render to the reference and provide specific feedback on how to better match or learn from the reference style, lighting, and composition.';
    }

    const openrouterApiKey = Deno.env.get('OPENROUTER_API_KEY');
    
    if (!openrouterApiKey) {
      const mockAnalysis = `## Overall Assessment\nThis is a demonstration of the Aetheria Render Analyzer. In production, this would provide detailed AI-powered feedback on your 3D render.\n\n## Lighting Analysis\nYour lighting setup shows potential. Consider experimenting with three-point lighting to add more depth and dimension to your scene.\n\n## Materials & Textures\nThe surface materials could benefit from more variation in roughness and metallic properties to achieve greater realism.\n\n## Composition\nThe composition follows good principles. The focal point is clear, though you might want to experiment with the rule of thirds for a more dynamic arrangement.\n\n## Technical Quality\nThe render quality is solid. If you notice any noise, consider increasing your sample count or using a denoiser.\n\n## Recommendations\n1. Adjust the key light intensity for better contrast\n2. Add subtle ambient occlusion for depth\n3. Refine material properties for enhanced realism\n4. Consider adding environmental details\n\n**Note:** To receive actual AI-powered analysis, configure your OpenRouter API key.`;

      return new Response(
        JSON.stringify({ analysis: mockAnalysis, score: 72 }),
        {
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
          },
        }
      );
    }

    const messages = [
      {
        role: 'system',
        content: systemPrompt
      },
      {
        role: 'user',
        content: [
          {
            type: 'text',
            text: userPrompt
          },
          {
            type: 'image_url',
            image_url: {
              url: renderImage
            }
          }
        ]
      }
    ];

    if (referenceImage) {
      messages[1].content.push({
        type: 'image_url',
        image_url: {
          url: referenceImage
        }
      });
    }

    const openrouterResponse = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openrouterApiKey}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://aetheria-render.com',
        'X-Title': 'Aetheria Render Analyzer'
      },
      body: JSON.stringify({
        model: 'anthropic/claude-3.5-sonnet',
        messages: messages,
        max_tokens: 2000,
        temperature: 0.7
      })
    });

    if (!openrouterResponse.ok) {
      throw new Error(`OpenRouter API error: ${openrouterResponse.statusText}`);
    }

    const result = await openrouterResponse.json();
    const analysis = result.choices[0]?.message?.content || 'Analysis could not be completed.';

    const scorePrompt = `Based on the analysis you just provided, rate this 3D render on a scale of 1-100 considering all aspects (lighting, materials, composition, technical quality, and artistic direction). Respond with ONLY a number between 1-100, nothing else.`;

    const scoreMessages = [
      {
        role: 'system',
        content: 'You are a 3D rendering expert. Respond with only a single number.'
      },
      {
        role: 'user',
        content: [
          {
            type: 'text',
            text: scorePrompt
          },
          {
            type: 'image_url',
            image_url: {
              url: renderImage
            }
          }
        ]
      }
    ];

    if (referenceImage) {
      scoreMessages[1].content.push({
        type: 'image_url',
        image_url: {
          url: referenceImage
        }
      });
    }

    const scoreResponse = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openrouterApiKey}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://aetheria-render.com',
        'X-Title': 'Aetheria Render Analyzer'
      },
      body: JSON.stringify({
        model: 'anthropic/claude-3.5-sonnet',
        messages: scoreMessages,
        max_tokens: 10,
        temperature: 0.3
      })
    });

    let score = null;
    if (scoreResponse.ok) {
      const scoreResult = await scoreResponse.json();
      const scoreText = scoreResult.choices[0]?.message?.content?.trim() || '';
      score = parseInt(scoreText, 10);
      if (isNaN(score)) score = null;
    }

    return new Response(
      JSON.stringify({ analysis, score }),
      {
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json',
        },
      }
    );

  } catch (error) {
    console.error('Error in analyze-render function:', error);
    
    return new Response(
      JSON.stringify({ 
        error: 'Failed to analyze render',
        details: error instanceof Error ? error.message : 'Unknown error'
      }),
      {
        status: 500,
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json',
        },
      }
    );
  }
});