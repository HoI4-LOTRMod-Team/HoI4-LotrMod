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
		}

		float3 hsv2rgb(float3 c)
		{
			float4 K = float4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
			float3 p = abs(frac(c.xxx + K.xyz) * 6.0 - K.www);
			return c.z * lerp(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
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
			for (int i = 0; i < 15; i++)
			{
				total += noise(n) * amplitude;
				n += n * 1.7;
				amplitude *= 0.47;
			}
			return total;
		}

		float4 flame(float2 fragCoord)
		{
			const float aspect_ratio = 0.56;

			fragCoord.y *= -1;
			fragCoord.y += aspect_ratio;

			const float3 c1 = float3(0.5, 0.0, 0.1);
			const float3 c2 = float3(0.9, 0.1, 0.0);
			const float3 c3 = float3(0.2, 0.1, 0.7);
			const float3 c4 = float3(1.0, 0.9, 0.1);
			const float3 c5 = float3(0.1, 0.1, 0.1);
			const float3 c6 = float3(0.9, 0.9, 0.9);

			float2 speed = float2(0.0, 0.2);
			float shift = 1.327;

			float vTime = 0.5*Time;

			float dist = 3.5 - sin(vTime * 0.4) / 1.89;

			float2 p = fragCoord.xy * dist;
			p.y -= vTime / 8;
			float q = fbm(p - vTime * 0.01 + 1.0 * sin(vTime) / 10.0);
			float q3 = fbm(p - vTime * 0.9 - 10.0 * cos(vTime) / 30.0) - 4.0;
			
			q = (2.2*q - 2.0 * q3) / 3.8;

			float2 r = float2(fbm(p + q / 2.0 + vTime * speed.x - p.x - p.y), fbm(p + q - vTime * speed.y));
			float3 c = lerp(c1, c2, fbm(p + r)) + lerp(c3, c4, r.x) - lerp(c5, c6, r.y);
			float3 color = float3(1,1,1) * c * cos(shift * fragCoord.y / aspect_ratio);

			// regulates frequency of bright flames
			color += 0.05;
			color.r *= 0.8;

			float3 hsv = rgb2hsv(color);
			hsv.y *= hsv.z * 1.1;
			hsv.z *= hsv.y * 1.13;
			hsv.y = (2.2 - hsv.z * 0.9) * 1.20;
			color = hsv2rgb(hsv);

			return float4(color.x, color.y, color.z, 1);
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

			

			float4 og_color = OutColor;// * Color;
			float4 flame_color = flame(v.vTexCoord.xy);

			flame_color = lerp(
				float4(0.0200, 0.0125, 0.00120, 0),
				float4(0.480, 0.292, 0.00960, 1),
				flame_color.r
			);

			float alpha = og_color.a;

			alpha = flame_color.a * 0.15 * length(flame_color.rg) * length(flame_color.rg);
			alpha = max(alpha, og_color.a-og_color.r*0.2);
			alpha = min(alpha, og_color.b);
			//alpha = 1;

			float4 og_color2 = float4(
				og_color.r + 0.042,
				0.028,
				0.011,
				og_color.a
			);

			float par = og_color.a;
			float4 ret = lerp(flame_color, og_color2, og_color.a*(par-par*og_color.r));

			ret.a = alpha;
			//ret.g = 1;
			return ret;

			//return flame_color;

			
			
			//OutColor.b = 1;//1.0f;//sin(vTime);
			//OutColor *= flame(v.vTexCoord.xy*1920);
			float old_a = OutColor.a;
			OutColor = lerp(OutColor, flame_color, OutColor.r*OutColor.a);
			OutColor.a = min(old_a, flame_color.r);
			//OutColor.g = 1;
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

