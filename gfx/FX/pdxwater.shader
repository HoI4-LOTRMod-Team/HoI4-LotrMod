Includes = {
	"constants.fxh"
	"standardfuncsgfx.fxh"
	"pdxmap.fxh"
	"shadow.fxh"
	"tiled_pointlights.fxh"
	"fow.fxh"
}

PixelShader =
{
	Samplers =
	{
		HeightTexture =
		{
			Index = 0
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		LeanTexture1 =
		{
			Index = 1
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		LeanTexture2 =
		{
			Index = 2
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		ProvinceSecondaryColorMap =
		{
			Index = 3
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		SpecularMap =
		{
			Index = 4
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		WaterRefraction =
		{
			Index = 5
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}
		IceDiffuse =
		{
			Index = 6
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		IceNoise =
		{
			Index = 7
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		ReflectionCubeMap =
		{
			Index = 8
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Clamp"
			AddressV = "Clamp"
			Type = "Cube"
		}
		SnowMudTexture =
		{
			Index = 9
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		LightIndexMap =
		{
			Index = 10
			MagFilter = "Point"
			MinFilter = "Point"
			MipFilter = "Point"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}
		LightDataMap =
		{
			Index = 11
			MagFilter = "Point"
			MinFilter = "Point"
			MipFilter = "Point"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}
		GradientBorderChannel1 =
		{
			Index = 12
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}
		GradientBorderChannel2 =
		{
			Index = 13
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}
		ShadowMap =
		{
			Index = 15
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
			Type = "Shadow"
		}
	}
}


VertexStruct VS_INPUT_WATER
{
    int2 position			: POSITION;
};

VertexStruct VS_OUTPUT_WATER
{
    float4 position			: PDX_POSITION;
	float3 pos				: TEXCOORD0;
	float2 uv				: TEXCOORD1;
	float4 screen_pos		: TEXCOORD2;
	float3 cubeRotation     : TEXCOORD3;
	float4 vShadowProj      : TEXCOORD4;
	float4 vScreenCoord		: TEXCOORD5;
	float2 uv_ice			: TEXCOORD6;
};


ConstantBuffer( 3, 48 )
{
	float3 vTime_HalfPixelOffset;
};



VertexShader =
{
	MainCode VertexShader
	[[
		VS_OUTPUT_WATER main( const VS_INPUT_WATER VertexIn )
		{
			VS_OUTPUT_WATER VertexOut;
			VertexOut.pos = float3( VertexIn.position.x, WATER_HEIGHT, VertexIn.position.y );
			VertexOut.position = mul( ViewProjectionMatrix, float4( VertexOut.pos.x, VertexOut.pos.y, VertexOut.pos.z, 1.0f ) );
			VertexOut.screen_pos = VertexOut.position;
			VertexOut.screen_pos.y = FIX_FLIPPED_UV( VertexOut.screen_pos.y );
			VertexOut.uv = float2( ( VertexIn.position.x + 0.5f ) / MAP_SIZE_X,  ( VertexIn.position.y + 0.5f - MAP_SIZE_Y ) / -MAP_SIZE_Y );
			VertexOut.uv *= float2( MAP_POW2_X, MAP_POW2_Y ); //POW2
			//VertexOut.uv *= 0.01;
			VertexOut.uv_ice = VertexOut.uv * float2( MAP_SIZE_X, MAP_SIZE_Y ) * 0.1f;
			VertexOut.uv_ice *= float2( FOW_POW2_X, FOW_POW2_Y ); //POW2

			float vAnimTime = vTime_HalfPixelOffset.x * 0.01f;
			VertexOut.cubeRotation = normalize( float3( sin( vAnimTime ) * 0.5f, sin( vAnimTime ), cos( vAnimTime ) * 0.3f ) );

			VertexOut.vShadowProj = mul( ShadowMapTextureMatrix, float4( VertexOut.pos, 1.0f ) );

			// Output the screen-space texture coordinates
			VertexOut.vScreenCoord.x = ( VertexOut.position.x * 0.5 + VertexOut.position.w * 0.5 );
			VertexOut.vScreenCoord.y = ( VertexOut.position.w * 0.5 - VertexOut.position.y * 0.5 );
		#ifdef PDX_OPENGL
			VertexOut.vScreenCoord.y = -VertexOut.vScreenCoord.y;
		#endif
			VertexOut.vScreenCoord.z = VertexOut.position.w;
			VertexOut.vScreenCoord.w = VertexOut.position.w;

			return VertexOut;
		}



	]]
}

PixelShader =
{
	MainCode PixelShader
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
		#define SEA_TIME (vTime_HalfPixelOffset.x * 0.1f * SEA_SPEED % 1000.0f)

		#define SEA_BASE float3(0.11f,0.19f,0.22f)
		#define SEA_WATER_COLOR float3(0.55f,0.9f,0.7f)

		#define iTime vTime_HalfPixelOffset.x * 0.1f % 1000.0f

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


		float4 waveShader(float2 fragCoord, float2 uv, VS_OUTPUT_WATER Input) {
			float4 fragColor;

			//float3 ret = getNormal(float3(uv.x, 0.0, uv.y), 0.01);
			//float3 ret = rgb2hsv(float3(0, 1, 0.0f));
			//float3 ret = float3(uv.x, uv.y, 0);
			//return float4(ret.x, ret.y, ret.z, 1);

			float2 iResolution = float2(2000, 1000);
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
			//float3 ori = vCamPos;//float3(0.0, 3.5, time * 3.0);
			float3 ori = float3(0.0, 3.5, time * 3.0);

			// Ray direction
			//float3 dir = normalize(Input.pos - vCamPos);//normalize(float3(uv.x, uv.y, -1.6));
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
















		float3 ApplyIce( float3 vColor, float2 vPos, inout float3 vNormal, float4 vMudSnowColor, float2 vIceUV, out float vIceFade )
		{
			float4 vIceDiffuse = tex2D( IceDiffuse, vIceUV );
			float vIceNoise = tex2D( IceNoise, ( vPos + 0.5f ) * ICE_NOISE_TILING ).r;

			float vSnow = saturate( GetSnow( vMudSnowColor ) - 0.0f );


			vIceFade = vSnow*8.0f;
			vIceFade *= vIceNoise;

			float vOpacity = 1 - cam_distance( ICE_CAM_MIN, ICE_CAM_MAX );
			vIceFade *= vOpacity;

			// Code below will remove ice from certain parts of the world
			float vMapLimitFade = saturate( saturate( (vPos.y/MAP_SIZE_Y) - 0.74f )*800.0f );
			vIceFade *= vMapLimitFade;

			vIceFade = saturate( ( vIceFade-0.3f ) * 10.0f );
			vNormal = normalize( lerp( vNormal, normalize( vIceDiffuse.rbg - 0.5f ), vIceFade ) );

			float3 vIceColor = ICE_COLOR * vIceDiffuse.a;
			vColor = lerp( vColor, vIceColor, vIceFade );

			return vColor;
		}
		float MultiSampleTexX( in sampler2D TexCh, in float2 vUV )
		{
		#ifdef LOW_END_GFX
			return tex2D( TexCh, vUV ).x;
		#else
			float vOffsetX = -0.5f / MAP_SIZE_X;
			float vOffsetY = -0.5f / MAP_SIZE_Y;
			float vResult = tex2D( TexCh, vUV ).x;
			vResult += tex2D( TexCh, vUV + float2( -vOffsetX, 0 ) ).x;
			vResult += tex2D( TexCh, vUV + float2( 0, -vOffsetY ) ).x;
			vResult += tex2D( TexCh, vUV + float2( vOffsetX, 0 ) ).x;
			vResult += tex2D( TexCh, vUV + float2( 0, vOffsetY ) ).x;
			vResult += tex2D( TexCh, vUV + float2( -vOffsetX, -vOffsetY ) ).x;
			vResult += tex2D( TexCh, vUV + float2(  vOffsetX, -vOffsetY ) ).x;
			vResult += tex2D( TexCh, vUV + float2(  vOffsetX,  vOffsetY ) ).x;
			vResult += tex2D( TexCh, vUV + float2( -vOffsetX,  vOffsetY ) ).x;
			vResult /= 9;
			return vResult;
		#endif
		}

		float4 main( VS_OUTPUT_WATER Input ) : PDX_COLOR
		{
			//return float4( 0, 0, 1, 1 );
			float waterHeight = MultiSampleTexX( HeightTexture, Input.uv ) / ( 95.7f / 255.0f );
			float waterShore = saturate( ( waterHeight - 0.954f ) * 25.0f );

			float2 B;
			float3 M;
			float3 normal;

			// LOTR NOTE: We multiply the UVs and Time for larger wave effect
			float2 nuv = float2(Input.uv.x*0.0065f, Input.uv.y*0.00455f);
			SampleWater( nuv, 0.2f*vTime_HalfPixelOffset.x, B, M, normal, LeanTexture1, LeanTexture2 );

			float vSpecMap = tex2D( SpecularMap, Input.uv ).a;
			normal.y += ( 1.0f - vSpecMap );
			normal.xz *= vSpecMap;
			normal = normalize( normal );

			float vFlatten = vSpecMap;
			B *= vFlatten*0.5f; // LOTR NOTE: Factor to lessen the sun glare
			M *= vFlatten * vFlatten;

		#ifdef LOW_END_GFX
			float3 SunDirWater = float3( 0, -1, 0 );
		#else
			float3 SunDirWater = CalculateSunDirectionWater( Input.pos );
			//float3 SunDirWater = float3( 0, -1, 0 ); // LOTR NOTE: Alternative way to do water
		#endif
			float3 H = normalize( normalize(vCamPos - Input.pos).xzy + -SunDirWater.xzy );
			float2 HWave = H.xy/H.z - B;

			float3 sigma = M - float3( B*B, B.x*B.y);
			float det = sigma.x*sigma.y - sigma.z*sigma.z;
			float e = HWave.x*HWave.x*sigma.y + HWave.y*HWave.y*sigma.x - 2*HWave.x*HWave.y*sigma.z;
			float spec = (det <= 0) ? 0.0f : exp( -0.5f*e/det ) / sqrt(det);

			float2 refractiveUV = ( Input.screen_pos.xy / Input.screen_pos.w ) * 0.5f + 0.5f;
			refractiveUV.y = 1.0f - refractiveUV.y;
			refractiveUV += vTime_HalfPixelOffset.gb;
			float vRefractionScale = saturate( 5.0f - ( Input.screen_pos.z / Input.screen_pos.w ) * 5.0f );

			float2 vRefractionDistortion = normal.xz * vRefractionScale * 1.80f;

			float3 vEyeDir = normalize( Input.pos - vCamPos.xyz );
			float3 reflection = reflect( vEyeDir, normal );

			float vSpecularIntensity = 0.01f;
			float vGlossiness = (spec/9.0f) * (1-vSpecMap);
			//float CubeMipmapIndex = GetEnvmapMipLevel(saturate(1.0f-vSpecMap));

			//float3 reflectiveColor = texCUBElod( ReflectionCubeMap, float4(reflection, CubeMipmapIndex) ).rgb;// * CubemapIntensity;
			float3 reflectiveColor = texCUBE( ReflectionCubeMap, reflection ).rgb;

		#ifdef NO_REFRACTIONS
			float3 og_refractiveColor = float3( 0, 0.1f, 0.2f );
		#else
			float3 og_refractiveColor = tex2D( WaterRefraction, refractiveUV.xy - vRefractionDistortion ).rgb;
		#endif
			float3 refractiveColor = og_refractiveColor;

			float fresnelBias = 0.4f; // CUBEMAP INTENSITY // LOTR: Lowered from 0.5f
			float fresnel = saturate( dot( -vEyeDir, normal ) ) * 0.5f;
			fresnel = saturate( fresnelBias + ( 1.0f - fresnelBias ) * pow( 1.0f - fresnel, 10.0) );
			refractiveColor = refractiveColor * ( 1.0f - fresnel ) + reflectiveColor * fresnel;

			float vIceFade = 0.0f;
		#ifndef LOW_END_GFX
			float4 vMudSnowColor = GetMudSnowColor( Input.pos, SnowMudTexture );
			refractiveColor = ApplyIce( refractiveColor, Input.pos.xz, normal, vMudSnowColor, Input.uv_ice, vIceFade );

			vRefractionDistortion *= 1.0f - vIceFade;
			vSpecularIntensity += vIceFade * 0.07f;
			vGlossiness += vIceFade * 20.0f;
		#endif

			float vBloomAlpha = 0.0f;

			// LOTR NOTE: This used to be here, now we do it further below
			//gradient_border_apply( refractiveColor, normal,
			//	Input.uv + vRefractionDistortion * 0.0075f,
			//	GradientBorderChannel1, GradientBorderChannel2, 0.0f,
			//	vGBCamDistOverride_GBOutlineCutoff.zw * GB_OUTLINE_CUTOFF_SEA,
			//	vGBCamDistOverride_GBOutlineCutoff.xy, vBloomAlpha );
			//secondary_color_mask( refractiveColor, normal,
			//	Input.uv - vRefractionDistortion * 0.001,
			//	ProvinceSecondaryColorMap,
			//	vBloomAlpha );

			LightingProperties lightingProperties;
			lightingProperties._WorldSpacePos = Input.pos;
			lightingProperties._ToCameraDir = normalize(vCamPos - Input.pos);
			lightingProperties._Normal = normal;
			lightingProperties._Diffuse = refractiveColor;
			lightingProperties._Glossiness = vGlossiness;
			lightingProperties._SpecularColor = vec3(vSpecularIntensity);
			lightingProperties._NonLinearGlossiness = GetNonLinearGlossiness(vGlossiness);


			// Grab the shadow term
		#ifdef LOW_END_GFX
			float3 diffuseLight = vec3(1.0f);
			float3 specularLight = vec3(0.002f);
		#else
			float3 diffuseLight = vec3(0.0);
			float3 specularLight = vec3(0.0);

			float4 vShadowCoord = Input.vScreenCoord;
			vShadowCoord.xz = vShadowCoord.xz + vRefractionDistortion * 20.0f;
			float fShadowTerm = GetShadowScaled( SHADOW_WEIGHT_WATER, vShadowCoord, ShadowMap );

			CalculateSunLight( lightingProperties, fShadowTerm, SunDirWater, diffuseLight, specularLight );

			CalculatePointLights( lightingProperties, LightDataMap, LightIndexMap, diffuseLight, specularLight);
		#endif

			float3 vOut = ComposeLight(lightingProperties, diffuseLight, specularLight);

		// LOTR NOTE: This used to be here, now we do it further below
		#ifndef LOW_END_GFX
			//vOut = ApplyFOW( vOut, ShadowMap, Input.vScreenCoord );
			//vOut = ApplyDistanceFog( vOut, Input.pos );
		#endif

			// LOTR NOTE: This used to be here, now we do it further below
			//vOut = DayNightWithBlend( vOut, CalcGlobeNormal( Input.pos.xz ), lerp(BORDER_NIGHT_DESATURATION_MAX, 1.0f, vBloomAlpha) );


			// LOTR STUFF

			// The lakes we want are marked as completely black on the Specular alpha channel
			float lake_fac = vSpecMap;
			lake_fac = min(lake_fac, 0.1f)*10.0f; // This takes every alp < 0.1 and interpolates it into [0,1]

			// For lakes, use the original refractiveColor (without specular and stuff). This makes them look more like rivers
			vOut.rgb = lerp(og_refractiveColor, vOut.rgb, lake_fac);

			gradient_border_apply( vOut, normal,
				Input.uv + vRefractionDistortion * 0.0075f,
				GradientBorderChannel1, GradientBorderChannel2, 0.0f,
				vGBCamDistOverride_GBOutlineCutoff.zw * GB_OUTLINE_CUTOFF_SEA,
				vGBCamDistOverride_GBOutlineCutoff.xy, vBloomAlpha );
			secondary_color_mask( vOut, normal,
				Input.uv - vRefractionDistortion * 0.001,
				ProvinceSecondaryColorMap,
				vBloomAlpha );

		#ifndef LOW_END_GFX
			vOut = ApplyFOW( vOut, ShadowMap, Input.vScreenCoord );
			vOut = ApplyDistanceFog( vOut, Input.pos );
		#endif

			vOut = DayNightWithBlend( vOut, CalcGlobeNormal( Input.pos.xz ), lerp(BORDER_NIGHT_DESATURATION_MAX, 1.0f, vBloomAlpha) );

			// papermap factor
			float map_fac = smoothstep(1800, 2600, vCamPos.y);

		#ifdef LOW_END_GFX
			DebugReturn(vOut, lightingProperties, 0.0f);
		#else
			DebugReturn(vOut, lightingProperties, fShadowTerm);
		#endif
			//return float4(vOut, (1.0f - waterShore)*(1.0f-map_fac));
			float2 wsUV = float2(
				Input.uv.x * 4000.0f,
				(1.0f - Input.uv.y) * 2000.0f
			);
			float2 wsrUV = float2(
				Input.uv.x,
				(1.0f - Input.uv.y)
			);
			return waveShader(wsrUV, wsrUV, Input);
		}
	]]
}


BlendState BlendState
{
	BlendEnable = yes
	AlphaTest = no
	SourceBlend = "src_alpha"
	DestBlend = "inv_src_alpha"
	WriteMask = "RED|GREEN|BLUE"
}

Effect water_low_gfx
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShader"
	Defines = { "LOW_END_GFX" "NO_REFRACTIONS" }
}

Effect water_no_refractions
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShader"
	Defines = { "NO_REFRACTIONS" }
}

Effect water
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShader"
}
