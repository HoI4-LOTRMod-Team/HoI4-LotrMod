Includes = {
	"buttonstate.fxh"
	"sprite_animation.fxh"
}

PixelShader =
{
	Samplers =
	{
		MapTexture =
		{
			Index = 0
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "None"
			AddressU = "Clamp"
			AddressV = "Clamp"
			MipMapLodBias = -0.8
		}
		MaskTexture =
		{
			Index = 1
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "None"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}
		AnimatedTexture =
		{
			Index = 2
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "None"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		MaskTexture2 =
		{
			Index = 3
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "None"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}
		AnimatedTexture2 =
		{
			Index = 4
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "None"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		#This masking texture is the ACTUAL masking texture. The others are for animation
		MaskingTexture =
		{
			Index = 5
			MagFilter = "Point"
			MinFilter = "Point"
			MipFilter = "None"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}




	}
}


VertexStruct VS_OUTPUT
{
	float4  vPosition : PDX_POSITION;
	float2  vTexCoord : TEXCOORD0;
@ifdef ANIMATED
	float4  vAnimatedTexCoord : TEXCOORD1;
@endif
@ifdef MASKING
	float2  vMaskingTexCoord : TEXCOORD2;
@endif
};


VertexShader =
{
	MainCode VertexShader
	[[
		VS_OUTPUT main(const VS_INPUT v )
		{
		    VS_OUTPUT Out;
		    Out.vPosition  = mul( WorldViewProjectionMatrix, float4( v.vPosition.xyz, 1 ) );
		
		    Out.vTexCoord = v.vTexCoord;
			Out.vTexCoord += Offset;
			
		#ifdef ANIMATED
			Out.vAnimatedTexCoord = GetAnimatedTexcoord(v.vTexCoord);	
		#endif

		#ifdef MASKING
			//A bit hacky, but we want the masking texture coordinates to be in the range [0,1]. We turn all 0's to 0 and all nonzero to 1.
			Out.vMaskingTexCoord = saturate(v.vTexCoord * 1000); 
		#endif
		
		    return Out;
		}
	]]
}

PixelShader =
{
	MainCode PixelShaderUp
	[[
		float rand(float2 n) {
			return frac(sin(cos(dot(n, float2(12.9898, 12.1414)))) * 83758.5453);
		}

		float3 rgb2hsv(float3 c)
		{
			float4 K = float4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
			float4 p = lerp(float4(c.b, c.g, K.w, K.z), float4(c.g, c.b, K.x, K.y), step(c.b, c.g));
			float4 q = lerp(float4(p.x, p.y, p.w, c.r), float4(c.r, p.y, p.z, p.x), step(p.x, c.r));

			float d = q.x - min(q.w, q.y);
			float e = 1.0e-10;
			return float3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
			//return float3(1,1,1);
		}

		float3 hsv2rgb(float3 c)
		{
			float4 K = float4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
			float3 p = abs(frac(c.xxx + K.xyz) * 6.0 - K.www);
			return c.z * lerp(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
			//return c.z * lerp(K.xxx, saturate(p - K.xxx, 0.0, 1.0), c.y);
			//return float3(1,1,1);
		}

		float noise(float2 n)
		{
			const float2 d = float2(0.0, 1.0);
			float2 b = floor(n), f = smoothstep(float2(0.0, 0.0), float2(1.0, 1.0), frac(n));
			return lerp(lerp(rand(b), rand(b + d.yx), f.x), lerp(rand(b + d.xy), rand(b + d.yy), f.x), f.y);
		}

		float fbm(float2 n)
		{
			float total = 0.0, amplitude = 1.0;
			for (int i = 0; i < 5; i++)
			{
				total += noise(n) * amplitude;
				n += n * 1.7;
				amplitude *= 0.47;
			}
			return total;
		}

		float4 flame(float2 fragCoord)
		{
			float2 iResolution = float2(1920, 1080);

			const float3 c1 = float3(0.5, 0.0, 0.1);
			const float3 c2 = float3(0.9, 0.1, 0.0);
			const float3 c3 = float3(0.2, 0.1, 0.7);
			const float3 c4 = float3(1.0, 0.9, 0.1);
			const float3 c5 = float3(0.1, 0.1, 0.1);
			const float3 c6 = float3(0.9, 0.9, 0.9);

			float2 speed = float2(0.2, 0.1);
			float shift = 1.327 + sin(Time * 2.0) / 2.4;
			float alpha = 1.0;

			float dist = 3.5 - sin(Time * 0.4) / 1.89;

			float2 p = fragCoord.xy * dist / iResolution.xx;
			p.x -= Time / 1.1;
			float q = fbm(p - Time * 0.01 + 1.0 * sin(Time) / 10.0);
			float qb = fbm(p - Time * 0.002 + 0.1 * cos(Time) / 5.0);
			float q2 = fbm(p - Time * 0.44 - 5.0 * cos(Time) / 7.0) - 6.0;
			float q3 = fbm(p - Time * 0.9 - 10.0 * cos(Time) / 30.0) - 4.0;
			float q4 = fbm(p - Time * 2.0 - 20.0 * sin(Time) / 20.0) + 2.0;
			q = (q + qb - 0.4 * q2 - 2.0 * q3 + 0.6 * q4) / 3.8;

			float2 r = float2(fbm(p + q / 2.0 + Time * speed.x - p.x - p.y), fbm(p + q - Time * speed.y));
			float3 c = lerp(c1, c2, fbm(p + r)) + lerp(c3, c4, r.x) - lerp(c5, c6, r.y);
			float3 color = float3(1,1,1) * c * cos(shift * fragCoord.y / iResolution.y);
			color += 0.05;
			color.r *= 0.8;

			float3 hsv = rgb2hsv(color);
			hsv.y *= hsv.z * 1.1;
			hsv.z *= hsv.y * 1.13;
			hsv.y = (2.2 - hsv.z * 0.9) * 1.20;
			color = hsv2rgb(hsv);

			return float4(color.x, color.y, color.z, alpha);
		}

		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
		    float4 OutColor = tex2D( MapTexture, v.vTexCoord );
			
		#ifdef ANIMATED
			OutColor = Animate(OutColor, v.vTexCoord, v.vAnimatedTexCoord, MaskTexture, AnimatedTexture, MaskTexture2, AnimatedTexture2);
		#endif

		#ifdef MASKING
			float4 MaskColor = tex2D( MaskingTexture, v.vMaskingTexCoord );
			OutColor.a *= MaskColor.a;
		#endif

			
			OutColor *= Color;
			//OutColor.b = 1;//1.0f;//sin(Time);
			OutColor *= flame(v.vTexCoord.xy*1920);
			return OutColor;
		}
		
	]]

	MainCode PixelShaderDown
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			return float4(0,0,0,0);
		}
	]]

	MainCode PixelShaderDisable
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
		    return float4(0,0,0,0);
		}	
	]]

	MainCode PixelShaderOver
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
		    return float4(0,0,0,0);
		}
	]]
}


BlendState BlendState
{
	BlendEnable = yes
	SourceBlend = "src_alpha"
	DestBlend = "inv_src_alpha"
}


Effect Up
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderUp"
}

Effect Down
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderDown"
}

Effect Disable
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderDisable"
}

Effect Over
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderOver"
}

