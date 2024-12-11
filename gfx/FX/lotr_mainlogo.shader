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
		// Constants
		static const float PI = 3.14159265358f;
		#define EPSILON_NRM (0.5 / iResolution.x)

		// Iterations
		static const int NUM_STEPS = 6;
		static const int ITER_GEOMETRY = 2;
		static const int ITER_FRAGMENT = 5	;

		// Sea properties
		static const float SEA_HEIGHT = 0.5;
		static const float SEA_CHOPPY = 3.0;
		static const float SEA_SPEED = 1.9;
		static const float SEA_FREQ = 0.24;
		#define SEA_TIME (Time * SEA_SPEED % 1000.0f)

		#define SEA_BASE float3(0.11f,0.19f,0.22f)
		#define SEA_WATER_COLOR float3(0.55f,0.9f,0.7f)

		#define iTime Time % 1000.0f

		float2x2 octave_m = float2x2(1.7, -1.2, 1.2, 1.4);

		float3 rgb2hsv(float3 c) {
			float4 K = float4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
			float4 p = lerp(float4(c.bg, K.wz), float4(c.gb, K.xy), step(c.b, c.g));
			float4 q = lerp(float4(p.xyw, c.r), float4(c.r, p.yzx), step(p.x, c.r));

			float d = q.x - min(q.w, q.y);
			float e = 1.0e-10;
			return float3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
		}

		float3 hsv2rgb(float3 c) {
			float4 K = float4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
			float3 p = abs(frac(c.xxx + K.xyz) * 6.0 - K.www);
			return c.z * lerp(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
		}

		float hash(float2 p) {
			float h = dot(p, float2(127.1, 311.7));
			return frac(sin(h) * 83758.5453123);
		}

		float noise(float2 p) {
			float2 i = floor(p);
			float2 f = frac(p);

			float2 u = f * f * (3.0 - 2.0 * f);

			return -1.0 + 2.0 * lerp(
				lerp(hash(i + float2(0.0, 0.0)), hash(i + float2(1.0, 0.0)), u.x),
				lerp(hash(i + float2(0.0, 1.0)), hash(i + float2(1.0, 1.0)), u.x),
				u.y
			);
		}

		float3x3 fromEuler(float3 ang) {
			float2 a1 = float2(sin(ang.x), cos(ang.x));
			float2 a2 = float2(sin(ang.y), cos(ang.y));
			float2 a3 = float2(sin(ang.z), cos(ang.z));
			float3x3 m;
			m[0] = float3(a1.y * a3.y + a1.x * a2.x * a3.x, a1.y * a2.x * a3.x + a3.y * a1.x, -a2.y * a3.x);
			m[1] = float3(-a2.y * a1.x, a1.y * a2.y, a2.x);
			m[2] = float3(a3.y * a1.x * a2.x + a1.y * a3.x, a1.x * a3.x - a1.y * a3.y * a2.x, a2.y * a3.y);
			return m;
		}


		float diffuse(float3 n, float3 l, float p) {
			return pow(dot(n, l) * 0.4 + 0.6, p);
		}

		float specular(float3 n, float3 l, float3 e, float s) {
			float nrm = (s + 8.0) / (3.1415 * 8.0);
			return pow(max(dot(reflect(e, n), l), 0.0), s) * nrm;
		}

		float3 getSkyColor(float3 e) {
			e.y = max(e.y, 0.0);
			float3 ret;
			ret.x = pow(1.0 - e.y, 2.0);
			ret.y = 1.0 - e.y;
			ret.z = 0.6 + (1.0 - e.y) * 0.4;
			return ret;
		}

		float sea_octave(float2 uv, float choppy) {
			uv += noise(uv);
			float2 wv = 1.0 - abs(sin(uv));
			float2 swv = abs(cos(uv));
			wv = lerp(wv, swv, wv);
			return pow(1.0 - pow(wv.x * wv.y, 0.65), choppy);
		}

		float map(float3 p) {
			float freq = SEA_FREQ;
			float amp = SEA_HEIGHT;
			float choppy = SEA_CHOPPY;
			float2 uv = p.xz; 
			uv.x *= 0.75;

			float h = 0.0;
			for (int i = 0; i < ITER_GEOMETRY; i++) {
				float d = sea_octave((uv + SEA_TIME) * freq, choppy);
				h += d * amp;

				float2x2 octave_m2 = float2x2(1.7, -1.2, 1.2, 1.4);
				uv = mul(uv, octave_m2);

				freq *= 1.9;
				amp *= 0.22;
				choppy = lerp(choppy, 1.0, 0.2);
			}
			return p.y - h;
		}

		float map_detailed(float3 p) {
			float freq = SEA_FREQ;
			float amp = SEA_HEIGHT;
			float choppy = SEA_CHOPPY;
			float2 uv = p.xz; 
			uv.x *= 0.75;

			float h = 0.0;
			for (int i = 0; i < ITER_FRAGMENT; i++) {
				float d = sea_octave((uv + SEA_TIME) * freq, choppy);
				d += sea_octave((uv - SEA_TIME) * freq, choppy);
				h += d * amp;

				//float2x2 scaled_octave_m = octave_m * (1.0 / 1.2);
				float2x2 octave_m2 = float2x2(1.7, -1.2, 1.2, 1.4);
				uv = mul(uv, octave_m2 / 1.2);

				freq *= 1.9;
				amp *= 0.22;
				choppy = lerp(choppy, 1.0, 0.2);
			}
			return p.y - h;
		}

		float3 getSeaColor(float3 p, float3 n, float3 l, float3 eye, float3 dist) {
			float fresnel = 1.0 - max(dot(n, -eye), 0.0);
			fresnel = pow(fresnel, 3.0) * 0.45;

			float3 reflected = getSkyColor(reflect(eye, n)) * 0.99;
			float3 refracted = SEA_BASE + diffuse(n, l, 80.0) * SEA_WATER_COLOR * 0.27;

			float3 color = lerp(refracted, reflected, fresnel);

			float atten = max(1.0 - dot(dist, dist) * 0.001, 0.0);
			color += SEA_WATER_COLOR * (p.y - SEA_HEIGHT) * 0.15 * atten;
			color += float3(1,1,1) * specular(n, l, eye, 90.0) * 0.5;

			return color;
		}

		float3 getNormal(float3 p, float eps) {
			float3 n;
			n.y = map_detailed(p);
			n.x = map_detailed(float3(p.x + eps, p.y, p.z)) - n.y;
			n.z = map_detailed(float3(p.x, p.y, p.z + eps)) - n.y;
			n.y = eps;
			return normalize(n);
		}

		
		float heightMapTracing(float3 ori, float3 dir, out float3 p) {
			float tm = 0.0;
			float tx = 500.0;
			//p = float3(0,0,0);

			float hx = map(ori + dir * tx);
			if (hx > 0.0) return tx;

			float hm = map(ori + dir * tm);

			float tmid = 0.0f;
			for (int i = 0; i < NUM_STEPS; i++) {
				tmid = lerp(tm, tx, hm / (hm - hx));
				p = ori + dir * tmid;

				float hmid = map(p);

				if (hmid < 0.0) {
					tx = tmid;
					hx = hmid;
				} else {
					tm = tmid;
					hm = hmid;
				}
			}
			return tmid;
		}


		float4 waveShader(float2 fragCoord, float2 uv ) {
			float4 fragColor;

			float3 ret = getNormal(float3(uv.x, 0.0, uv.y), 0.01);
			//float3 ret = rgb2hsv(float3(0, 1, 0.0f));
			//float3 ret = float3(uv.x, uv.y, 0);
			//return float4(ret.x, ret.y, ret.z, 1);

			float2 iResolution = float2(2000, 500);
			fragCoord *= iResolution;
			float2 iMouse = float2(0,0);
			//return float4(fragCoord.x, fragCoord.y, 0, 1);

			// Normalize pixel coordinates
			//float2 uv = fragCoord / iResolution.xy;
			uv = fragCoord / iResolution.xy;
			uv = uv * 2.0 - float2(1.0, 1.0);
			uv.x *= iResolution.x / iResolution.y;

			// Time-based animation
			float time = iTime * 2.7;

			// Camera rotation angles
			float roll = PI + sin(iTime) / 14.0 + cos(iTime / 2.0) / 14.0;
			float pitch = PI * 1.021 + (sin(iTime / 2.0) + cos(iTime)) / 40.0 
						+ ((iMouse.y / iResolution.y) - 0.8) * PI / 3.0;
			float yaw = (iMouse.x / iResolution.x) * PI * 4.0;
			float3 ang = float3(roll, pitch, yaw);

			// Camera origin
			float3 ori = float3(0.0, 3.5, time * 3.0);

			// Ray direction
			float3 dir = normalize(float3(uv.x, uv.y, -1.6));
			dir = mul(fromEuler(ang), dir);

			// Trace the ray
			float3 p;
			heightMapTracing(ori, dir, p);

			// Compute distance and normal
			float3 dist = float3(p.x - ori.x, p.y - ori.y, p.z - ori.z);
			float eps = dot(dist, dist) * EPSILON_NRM;
			float3 n = getNormal(p, eps);

			// Light direction
			float3 light = normalize(float3(0.0, 1.0, 0.8));

			// Get sky and sea colors
			float3 skyColor = getSkyColor(dir);
			float3 seaColor = getSeaColor(p, n, light, dir, dist);

			// Apply distance falloff for sea color
			seaColor = seaColor / sqrt(sqrt(length(dist)));

			// Daytime-specific color adjustments
			seaColor = seaColor * sqrt(sqrt(seaColor)) * 4.0;
			skyColor = skyColor * 1.05 - float3(0.03, 0.03, 0.03);

			// Contrast adjustment for sky
			skyColor = skyColor * skyColor;

			// Adjust sea color based on brightness
			float3 seaHsv = rgb2hsv(seaColor);
			if (seaHsv.z > 0.75 && length(dist) < 50.0) {
				seaHsv.z -= (0.9 - seaHsv.z) * 1.3;
			}
			seaColor = hsv2rgb(seaHsv);

			// Mix sky and sea colors with fog effect
			float fogFactor = pow(smoothstep(0.0, -0.05, dir.y), 0.3);
			float3 color = lerp(skyColor, seaColor, fogFactor);

			// Final color adjustments
			fragColor = float4(pow(color, float3(0.75, 0.75, 0.75)), 1.0);
			float3 hsv = rgb2hsv(fragColor.xyz);
			hsv.y += 0.131;
			hsv.z *= sqrt(hsv.z) * 1.1;

			// Daytime hue and brightness adjustments
			hsv.z *= 0.9;
			hsv.x -= hsv.z / 10.0;
			hsv.x += 0.02 + hsv.z / 50.0;
			hsv.z *= 1.01;
			hsv.y += 0.07;

			// Convert back to RGB
			fragColor.xyz = hsv2rgb(hsv);

			return fragColor;

			
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

			v.vTexCoord.y = 1.0f - v.vTexCoord.y;
			float4 ret = waveShader(v.vTexCoord.xy, v.vTexCoord.xy);
			//ret.g = 1;
			return ret;

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

