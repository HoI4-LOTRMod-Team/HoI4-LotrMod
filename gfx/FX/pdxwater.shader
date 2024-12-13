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
		static const float k_screenshotTime = 13.0;
		static const int k_raymarchSteps = 96;
		static const int k_fmbSteps = 3;
		static const int k_superSampleCount = 10;
		static const int k_fmbWaterSteps = 4;
		#define OBJ_ID_SKY 0.0
		#define OBJ_ID_GROUND 1.0
		#define g_fTime 0.2f*vTime_HalfPixelOffset.x
		static const float3 g_vSunDir = float3( -100.0, 70., 25. );
		float3 GetSunDir() { return normalize( g_vSunDir ); }

		static const float3 g_sunColour = float3( 1.0, 0.85, 0.5 ) * 5.0;
		static const float3 g_skyColour = float3( 0.1, 0.5, 1.0 ) * 1.0;
		static const float3 k_bgSkyColourUp = g_skyColour * 4.0;
		static const float3 k_bgSkyColourDown = g_skyColour * 6.0;
		static const float3 k_envFloorColor = float3(0.3, 0.2, 0.2);
		static const float3 k_vFogExt = float3(0.01, 0.015, 0.015) * 3.0;
		static const float3 k_vFogIn = float3(1.0, 0.9, 0.8) * 0.015;

		#define MOD2 float2(4.438975,3.972973)

		float Hash( float p ) {
			float2 p2 = frac(float2(p, p) * MOD2);
			p2 += dot(p2.yx, p2.xy+19.19);
			return frac(p2.x * p2.y);    
		}

		float2 Hash2( float p ) {
			float3 p3 = frac(float3(p, p, p) * float3(.1031, .1030, .0973));
			p3 += dot(p3, p3.yzx + 19.19);
			return frac((p3.xx+p3.yz)*p3.zy);
		}


		float SmoothNoise(in float2 o) {
			float2 p = floor(o);
			float2 f = frac(o);
			float n = p.x + p.y*57.0;
			float a = Hash(n+  0.0);
			float b = Hash(n+  1.0);
			float c = Hash(n+ 57.0);
			float d = Hash(n+ 58.0);
			float2 f2 = f * f;
			float2 f3 = f2 * f;
			float2 t = 3.0 * f2 - 2.0 * f3;
			float u = t.x;
			float v = t.y;
			float res = a + (b-a)*u +(c-a)*v + (a-b+d-c)*u*v;
			return res;
		}


		float FBM( float2 p, float ps ) {
			float f = 0.0;
			float tot = 0.0;
			float a = 1.0;
			for( int i=0; i < k_fmbSteps; i++) {
				f += SmoothNoise( p ) * a;
				p *= 2.0;
				tot += a;
				a *= ps;
			}
			return f / tot;
		}


		float3 SmoothNoise_DXY(in float2 o) {
			float2 p = floor(o);
			float2 f = frac(o);
			float n = p.x + p.y*57.0;
			float a = Hash(n+  0.0);
			float b = Hash(n+  1.0);
			float c = Hash(n+ 57.0);
			float d = Hash(n+ 58.0);
			float2 f2 = f * f;
			float2 f3 = f2 * f;
			float2 t = 3.0 * f2 - 2.0 * f3;
			float2 dt = 6.0 * f - 6.0 * f2;
			float u = t.x;
			float v = t.y;
			float du = dt.x;	
			float dv = dt.y;
			float res = a + (b-a)*u +(c-a)*v + (a-b+d-c)*u*v;
			float dx = (b-a)*du + (a-b+d-c)*du*v;
			float dy = (c-a)*dv + (a-b+d-c)*u*dv; 
			return float3(dx, dy, res);
		}


		float3 FBM_DXY( float2 p, float2 flow, float ps, float df ) {
			float3 f = float3(0.0, 0.0, 0.0);
			float tot = 0.0;
			float a = 1.0;
			for( int i=0; i<k_fmbWaterSteps; i++) {
				p += flow;
				flow *= -0.75; 
				float3 v = SmoothNoise_DXY( p );
				f += v * a;
				p += v.xy * df;
				p *= 2.0;
				tot += a;
				a *= ps;
			}
			return f / tot;
		}

		
		float GetTerrainHeight( const float3 vPos ) {    
			float fbm = FBM( vPos.xz * float2(0.5, 1.0), 0.5 );
			float fTerrainHeight = fbm * fbm * 0.05;
			fTerrainHeight -= 0.3 + (0.5 + 0.5 * sin( vPos.z * 0.001 + 3.0)) * 0.4;
			return fTerrainHeight;
		}


		float GetSceneDistance( const float3 vPos ) {
			return vPos.y - GetTerrainHeight( vPos );
		}

		float GetFlowDistance( const float2 vPos ) {
			return -GetTerrainHeight( float3( vPos.x, 0.0, vPos.y ) );
		}

		float2 GetBaseFlow( const float2 vPos ) {
			return float2( 1.0, 0.);
		}

		float2 GetGradient( const float2 vPos ) {
			float2 vDelta = float2(0.01, 0.00);
			float dx = GetFlowDistance( vPos + vDelta.xy ) - GetFlowDistance( vPos - vDelta.xy );
			float dy = GetFlowDistance( vPos + vDelta.yx ) - GetFlowDistance( vPos - vDelta.yx );
			return float2( dx, dy );
		}

		float4 SampleWaterNormal( float2 vUV, float2 vFlowOffset, float fMag ) {    
			float2 vFilterWidth = max(abs(ddx(vUV)), abs(ddy(vUV)));
			float fFilterWidth= max(vFilterWidth.x, vFilterWidth.y);
			float fScale = (1.0 / (1.0 + fFilterWidth * fFilterWidth * 2000.0));
			float fGradientAscent = 0.25 ;
			float3 dxy = FBM_DXY(vUV * 20.0, vFlowOffset * 20.0, 0.75, fGradientAscent);
			float3 vBlended = lerp( float3(0.0, 1.0, 0.0), normalize( float3(dxy.x, fMag, dxy.y) ), fScale );
			return float4( normalize( vBlended ), dxy.z * fScale );
		}

		float4 SampleFlowingNormal( const float2 vUV, const float2 vFlowRate, const float time ) {
			float fMag = 2.5 / (1.0 + dot( vFlowRate, vFlowRate ) * 5.0);
			float t0 = frac( time );
			float t1 = frac( time + 0.5 );
			
			float i0 = floor( time );
			float i1 = floor( time + 0.5 );
			
			float o0 = t0 - 0.5;
			float o1 = t1 - 0.5;
			
			float2 vUV0 = vUV + Hash2(i0);
			float2 vUV1 = vUV + Hash2(i1);
			
			float4 sample0 = SampleWaterNormal( vUV0, vFlowRate * o0, fMag );
			float4 sample1 = SampleWaterNormal( vUV1, vFlowRate * o1, fMag );

			float weight = abs( t0 - 0.5 ) * 2.0;
			float4 result=  lerp( sample0, sample1, weight );
			result.xyz = normalize(result.xyz);

			return result;
		}

		float3 ApplyVignetting( const in float2 vUV, const in float3 vInput ){
			float2 vOffset = (vUV - 0.5) * sqrt(2.0);
			float fDist = dot(vOffset, vOffset);
			const float kStrength = 0.8;
			float fShade = lerp( 1.0, 1.0 - kStrength, fDist );	
			return vInput * fShade;
		}

		float3 Tonemap( float3 x ) {
			float a = 0.010;
			float b = 0.132;
			float c = 0.010;
			float d = 0.163;
			float e = 0.101;
			return ( x * ( a * x + b ) ) / ( x * ( c * x + d ) + e );
		}

		struct Intersection {
			float m_dist;
			float m_objId;
			float3 m_pos;
		};
			
		void RaymarchScene( float3 vRayOrigin, float3 vRayDir, float near, float far, out Intersection intersection ) {
			float stepScale = 1.0;
			intersection.m_dist = near;
			intersection.m_objId = OBJ_ID_SKY;
			float sceneDist = 0.0;
			
			for( int iter = 0; iter < k_raymarchSteps; iter++ ) {
				float3 vPos = vRayOrigin + vRayDir * intersection.m_dist;
				sceneDist = GetSceneDistance( vPos );
				intersection.m_dist += sceneDist * stepScale;
				intersection.m_objId = OBJ_ID_GROUND;
				if ( sceneDist <= 0.01 ) {
					break;
				}
				if ( intersection.m_dist > far ) {
					intersection.m_objId = OBJ_ID_SKY;
					intersection.m_dist = far;
					break;
				}
			}
			intersection.m_pos = vRayOrigin + vRayDir * intersection.m_dist;
		}

		float3 GetSceneNormal(const in float3 vPos) {
			const float fDelta = 0.001;

			float3 vDir1 = float3( 1.0, 0.0, -1.0);
			float3 vDir2 = float3(-1.0, 0.0,  1.0);
			float3 vDir3 = float3(-1.0, 0.0, -1.0);
			
			float3 vOffset1 = vDir1 * fDelta;
			float3 vOffset2 = vDir2 * fDelta;
			float3 vOffset3 = vDir3 * fDelta;

			float3 vPos1 = vPos + vOffset1;
			float3 vPos2 = vPos + vOffset2;
			float3 vPos3 = vPos + vOffset3;
		
			float f1 = GetSceneDistance( vPos1 );
			float f2 = GetSceneDistance( vPos2 );
			float f3 = GetSceneDistance( vPos3 );
			
			vPos1.y -= f1;
			vPos2.y -= f2;
			vPos3.y -= f3;
			
			float3 vNormal = cross( vPos1 - vPos2, vPos3 - vPos2 );
			
			return normalize( vNormal );
		}



		void TraceWater( float3 vRayOrigin, float3 vRayDir, float near, float far, out Intersection intersection ) {
			intersection.m_dist = far;
			intersection.m_objId = 0;
			
			
			float t = -vRayOrigin.y / vRayDir.y;
			if ( t > 0.0 )  {
				intersection.m_dist = t;
			}
			intersection.m_pos = vRayOrigin + vRayDir * intersection.m_dist;
		}


		float tri(in float x){return abs(frac(x)-.5);}
		float3 tri3(in float3 p){return float3( tri(p.z+tri(p.y)), tri(p.z+tri(p.x)), tri(p.y+tri(p.x)));}
		float triNoise(in float3 p) {
			float z = 1.4;
			float rz = 0.;
			float3 bp = p;
			for (float i=0.; i<=4.; i++ ) {
				p += tri3(bp*2.);
				bp *= 1.8;
				z *= 1.5;
				p *= 1.2;
				rz+= (tri(p.z+tri(p.x+tri(p.y))))/z;
				bp += 0.14;
			}
			return rz;
		} 

		struct Surface {
			float3 m_pos;
			float3 m_normal;
			float3 m_albedo;
			float3 m_specR0;
			float m_gloss;
			float m_specScale;
		};

		void GetSurfaceInfo( Intersection intersection, out Surface surface ) {
			surface.m_pos = intersection.m_pos;
			surface.m_normal = GetSceneNormal(intersection.m_pos);
			float3 vNoisePos = surface.m_pos * float3(0.4, 0.3, 1.0);
			surface.m_normal = normalize(surface.m_normal + (vNoisePos));
			float fNoise = triNoise(vNoisePos);
			fNoise = pow( fNoise, 0.15);
			surface.m_albedo = lerp(float3(.7,.8,.95), float3(.1, .1,.05), fNoise );
			surface.m_specR0 = float3(0.001, 0.001, 0.001);
			surface.m_gloss = 0.0;
			surface.m_specScale = 1.0;
		}
		
		float GIV( float dotNV, float k) {
			return 1.0 / ((dotNV + 0.0001) * (1.0 - k)+k);
		}

		void AddSunLight( Surface surf, const float3 vViewDir, const float fShadowFactor, inout float3 vDiffuse, inout float3 vSpecular ) {
			float3 vSunDir = GetSunDir();
			float3 vH = normalize( vViewDir + vSunDir );
			float fNdotL = clamp(dot(GetSunDir(), surf.m_normal), 0.0, 1.0);
			float fNdotV = clamp(dot(vViewDir, surf.m_normal), 0.0, 1.0);
			float fNdotH = clamp(dot(surf.m_normal, vH), 0.0, 1.0);
			float diffuseIntensity = fNdotL;
			vDiffuse += g_sunColour * diffuseIntensity * fShadowFactor;
			float alpha = 1.0 - surf.m_gloss;
			float alphaSqr = alpha * alpha;
			float pi = 3.14159;
			float denom = fNdotH * fNdotH * (alphaSqr - 1.0) + 1.0;
			float d = alphaSqr / (pi * denom * denom);
			float k = alpha / 2.0;
			float vis = GIV(fNdotL, k) * GIV(fNdotV, k);
			float fSpecularIntensity = d * vis * fNdotL;
			vSpecular += g_sunColour * fSpecularIntensity * fShadowFactor;
		}
			
		void AddSkyLight( Surface surf, inout float3 vDiffuse, inout float3 vSpecular ) {
			float skyIntensity = max( 0.0, surf.m_normal.y * 0.3 + 0.7 );
			vDiffuse += g_skyColour * skyIntensity;       
		}

		float3 GetFresnel( float3 vView, float3 vNormal, float3 vR0, float fGloss ) {
			float NdotV = max( 0.0, dot( vView, vNormal ) );
			return vR0 + (float3(1.0, 1.0, 1.0) - vR0) * pow( 1.0 - NdotV, 5.0 ) * pow( fGloss, 20.0 );
		}

		float3 GetWaterExtinction( float dist ) {
			float fOpticalDepth = dist * 6.0;
			float3 vExtinctCol = 1.0 - float3(0.5, 0.4, 0.1);           
			float3 vExtinction = exp2( -fOpticalDepth * vExtinctCol );
			return vExtinction;
		}

		float3 GetSkyColour( float3 vRayDir ) {    
			float3 vSkyColour = lerp( k_bgSkyColourDown, k_bgSkyColourUp, clamp( vRayDir.y, 0.0, 1.0 ) );
			float fSunDotV = dot(GetSunDir(), vRayDir);    
			float fDirDot = clamp(fSunDotV * 0.5 + 0.5, 0.0, 1.0);
			vSkyColour += g_sunColour * (1.0 - exp2(fDirDot * -0.5)) * 2.0;
			
			return vSkyColour;
		}

		float3 GetEnvColour( float3 vRayDir, float fGloss ) {
			return lerp( k_envFloorColor, k_bgSkyColourUp, clamp( vRayDir.y * (1.0 - fGloss * 0.5) * 0.5 + 0.5, 0.0, 1.0 ) );
		}


		float3 GetRayColour( const in float3 vRayOrigin, const in float3 vRayDir,const in float near, const in float far, out Intersection intersection ){
			RaymarchScene( vRayOrigin, vRayDir, near, far, intersection );        
			if ( intersection.m_objId == OBJ_ID_SKY ){
				return GetSkyColour( vRayDir );
			}
			
			Surface surface;
			GetSurfaceInfo( intersection, surface );

			float3 vIgnore = float3(0.0, 0.0, 0.0);
			float3 vResult = float3(0.0, 0.0, 0.0);
			float fSunShadow = 1.0;
			AddSunLight( surface, -vRayDir, fSunShadow, vResult, vIgnore );
			AddSkyLight( surface, vResult, vIgnore);
			return vResult * surface.m_albedo;
		}

		float3 GetRayColour( const in float3 vRayOrigin, const in float3 vRayDir, const in float near, const in float far) {
			Intersection intersection;
			return GetRayColour( vRayOrigin, vRayDir, near, far, intersection );
		}

		float3 GetScene( const in float3 vRayOrigin,  const in float3 vRayDir, const in float near, const in float far) {
			float fSunDotV = dot(GetSunDir(), vRayDir);    
			Intersection waterInt;
			
			TraceWater( vRayOrigin, vRayDir, near, far, waterInt );
			float3 vReflectRayOrigin;
			float3 vResult;
			float3 vTransmitLight;
			Surface specSurface;
			float3 vSpecularLight = float3(0.0, 0.0, 0.0);
			float2 vFlowRate = GetBaseFlow( waterInt.m_pos.xz ) * 0.3;
			float4 vWaterNormalAndHeight = SampleFlowingNormal( waterInt.m_pos.xz, vFlowRate, g_fTime / 5.0 );
			float fFogDistance = waterInt.m_dist;
			float3 vWaterNormal = vWaterNormalAndHeight.xyz;
			vReflectRayOrigin = waterInt.m_pos;
			float3 vRefractRayOrigin = waterInt.m_pos;
			float3 vRefractRayDir = refract( vRayDir, vWaterNormal, 1.0 / 1.3333 );
			Intersection refractInt;
			float3 vRefractLight = GetRayColour( vRefractRayOrigin, vRefractRayDir, near, far, refractInt ); 

			
			float3 vExtinction = GetWaterExtinction( refractInt.m_dist + abs( refractInt.m_pos.y ) );
			specSurface.m_pos = waterInt.m_pos;
			specSurface.m_normal = normalize( vWaterNormal );
			specSurface.m_albedo = float3(1.0, 1.0, 1.0);
			specSurface.m_specR0 = float3( 0.01, 0.01, 0.01 );
			float2 vFilterWidth = max(abs(ddx(waterInt.m_pos.xz)), abs(ddy(waterInt.m_pos.xz)));
			float fFilterWidth= max(vFilterWidth.x, vFilterWidth.y);
			float fGlossFactor = exp2( -fFilterWidth * 0.3 );
			specSurface.m_gloss = 0.99 * fGlossFactor;            
			specSurface.m_specScale = 1.0;
			float3 vSurfaceDiffuse = float3(0.0, 0.0, 0.0);
			float fSunShadow = 1.0;
			AddSunLight( specSurface, -vRayDir, fSunShadow, vSurfaceDiffuse, vSpecularLight);
			AddSkyLight( specSurface, vSurfaceDiffuse, vSpecularLight);
			float3 vInscatter = vSurfaceDiffuse * (1.0 - exp( -refractInt.m_dist * 0.1 )) * (1.0 + fSunDotV);
			vTransmitLight = vRefractLight.rgb;
			vTransmitLight += vInscatter;
			vTransmitLight *= vExtinction; 
			float3 vReflectRayDir = reflect( vRayDir, vWaterNormal );
			float3 vReflectLight = GetRayColour( vReflectRayOrigin, vReflectRayDir, near, far );
			vReflectLight = lerp( GetEnvColour(vReflectRayDir, specSurface.m_gloss), vReflectLight, pow( specSurface.m_gloss, 40.0) );
			float3 vFresnel = GetFresnel( -vRayDir, vWaterNormal, specSurface.m_specR0, specSurface.m_gloss );
			vSpecularLight += vReflectLight;
			vResult = lerp(vTransmitLight, vSpecularLight, vFresnel * specSurface.m_specScale );
			float3 vFogColour = GetSkyColour(vRayDir);
			float3 vFogExtCol = exp2( k_vFogExt * -fFogDistance );
			float3 vFogInCol = exp2( k_vFogIn * -fFogDistance );
			vResult = vResult*(vFogExtCol) + vFogColour*(1.0-vFogInCol);
			return vResult;
		}


		void initCamera(out float3 ro, out float3 rd,out float near, out float far, float2 fcoord) {
			
			float3 lookAt = float3(0.,0.,0.);
			float3 cameraPosition = float3(1.5, 1.5, -1.5); 

			float3 iMouse = float3(0,0,0);
			float2 iResolution = float2(800, 450);
			
			
			if( iMouse.z > 0.0 )  {
				float fHeading = iMouse.x * 10.0 / iResolution.x;
				float fDist = 5.0 - iMouse.y * 5.0 / iResolution.y;
				cameraPosition.y += 1.0 + fDist * fDist * 0.05;
				cameraPosition.x += sin( fHeading ) * fDist;
				cameraPosition.z += cos( fHeading ) * fDist;
			}
			
			
			float3 forward = normalize(lookAt-cameraPosition);
			float3 right = normalize(float3(forward.z, 0., -forward.x ));
			float3 up = normalize(cross(forward,right));
			float FOV = 0.5;
			float2 aspect = float2(iResolution.x/iResolution.y, 1.0);
			near = 0.01;
			far = 200.0;
			float2 screenCoords = (2.0*fcoord.xy/iResolution.xy - 1.0)*aspect;
			ro = cameraPosition;
			rd = normalize(forward + FOV*screenCoords.x*right + FOV*screenCoords.y*up);
		}

		float4 waves_img(float2 fragCoord, float3 CamPos, float3 FragPos) {
			float4 fragColor = float4(0,0,0,1);

			float2 iResolution = float2(800, 450);

			float3 ro,rd; 
			float near, far;
			initCamera(ro, rd, near, far, fragCoord);

			//ro = CamPos;
			//rd = normalize(FragPos);//float3(0,0,1);//normalize(FragPos - CamPos);
			//near = 100.0;
			//far = 1000.0;

			float3 vResult = GetScene(ro, rd, near, far);
			//vResult = ApplyVignetting( fragCoord.xy / iResolution.xy, vResult );	
			float3 vFinal = Tonemap(vResult * 3.0);
			vFinal = vFinal * 1.1 - 0.1;
			fragColor = float4(vFinal, 1.0);

			return pow(fragColor, 2.0);
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
			Input.uv.y = 1.0 - Input.uv.y;
			return waves_img(Input.uv*float2(800,450), vCamPos, Input.pos);

			// Both of these values give a measure of how close we are to shore
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
			return float4(vOut, (1.0f - waterShore)*(1.0f-map_fac));
			//float2 wsUV = float2(
			//	Input.uv.x * 4000.0f,
			//	(1.0f - Input.uv.y) * 2000.0f
			//);
			//float2 wsrUV = float2(
			//	Input.uv.x,
			//	(1.0f - Input.uv.y)
			//);
			//return waveShader(wsrUV, wsrUV, Input);
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
