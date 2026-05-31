Includes = {
	"constants.fxh"
	"standardfuncsgfx.fxh"
	"shadow.fxh"
	"tiled_pointlights.fxh"
	"fow.fxh"
}

PixelShader =
{
	Samplers =
	{
		DiffuseMap =
		{
			Index = 0
			#MipMapLodBias = -1.0
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		SpecularMap =
		{
			Index = 1
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		NormalMap =
		{
			Index = 2
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		FlagMap =
		{
			Index = 3
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "None"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		SnowMudData =
		{
			Index = 4
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		IntelMap =
		{
			Index = 5
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}
		FOWNoise =
		{
			Index = 6
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		EnvironmentMap =
		{
			Index = 7
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Clamp"
			AddressV = "Clamp"
			Type = "Cube"
		}
		LightIndexMap =
		{
			Index = 8
			MagFilter = "Point"
			MinFilter = "Point"
			MipFilter = "Point"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}
		LightDataMap =
		{
			Index = 9
			MagFilter = "Point"
			MinFilter = "Point"
			MipFilter = "Point"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}
		GradientBorderChannel1 =
		{
			Index = 10
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}
		GradientBorderChannel2 =
		{
			Index = 11
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}	
		ProvinceSecondaryColorMap =
		{
			Index = 12
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		FOWHeight =
		{
			Index = 13
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "Linear"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
	}
}


VertexStruct VS_INPUT_PDXMESHSTANDARD
{
    float3 vPosition		: POSITION;
	float3 vNormal      	: TEXCOORD0;
	float4 vTangent			: TEXCOORD1;
	float2 vUV0				: TEXCOORD2;
@ifdef PDX_MESH_UV1
	float2 vUV1				: TEXCOORD3;
@endif
};

VertexStruct VS_INPUT_PDXMESHSTANDARD_SKINNED
{
    float3 vPosition		: POSITION;
	float3 vNormal      	: TEXCOORD0;
	float4 vTangent			: TEXCOORD1;
	float2 vUV0				: TEXCOORD2;
@ifdef PDX_MESH_UV1
	float2 vUV1				: TEXCOORD3;
@endif
	uint4 vBoneIndex 		: TEXCOORD4;
	float3 vBoneWeight		: TEXCOORD5;
};

VertexStruct VS_OUTPUT_PDXMESHSTANDARD
{
    float4 vPosition	: PDX_POSITION;
	float3 vNormal		: TEXCOORD0;
	float3 vTangent		: TEXCOORD1;
	float3 vBitangent	: TEXCOORD2;
	float2 vUV0			: TEXCOORD3;
	float2 vUV1			: TEXCOORD4;
	float4 vPos_Height	: TEXCOORD5;
};

VertexStruct VS_OUTPUT_PDXMESHSHADOW
{
    float4 vPosition	: PDX_POSITION;
	float4 vDepthUV0	: TEXCOORD0;
};

VertexStruct VS_INPUT_DEBUGNORMAL
{
    float3 vPosition		: POSITION;
	float3 vNormal      	: TEXCOORD0;
	float4 vTangent			: TEXCOORD1;
	float2 vUV0				: TEXCOORD2;
	float2 vUV1				: TEXCOORD3;
	float  vOffset      	: TEXCOORD6;
};

VertexStruct VS_INPUT_DEBUGNORMAL_SKINNED
{
    float3 vPosition		: POSITION;
	float3 vNormal      	: TEXCOORD0;
	float4 vTangent			: TEXCOORD1;
	float2 vUV0				: TEXCOORD2;
	float2 vUV1				: TEXCOORD3;
	uint4 vBoneIndex		: TEXCOORD4;
	float3 vBoneWeight		: TEXCOORD5;
	float  vOffset      	: TEXCOORD6;
};

VertexStruct VS_OUTPUT_DEBUGNORMAL
{
    float4 vPosition : PDX_POSITION;
	float2 vUV0		 : TEXCOORD0;
	float  vOffset	 : TEXCOORD1;
};


ConstantBuffer( 1, 28 )
{
	float4x4 WorldMatrix;
	float4 AtlasCoordinate;
	float vUVAnimSpeed;
};

#// this const buffer is only valid for trains
ConstantBuffer( 1, 28 )
{
	float4x4 WorldMatrix2; // an alias of WorldMatrix. i have to put a matrix here to shift train user data by 4x4 matrix since WorldMatrix is actually valud and being used
	float4 TrainColor;
	float2 TrainAlphaStart;
	float2 TrainAlphaDir;
};

ConstantBuffer( 2, 41 )
{
	float4x4 matBones[50]; // : Bones :register( c41 ); // 50 * 4 registers 41 - 241 
};


Code
[[

static const int PDXMESH_MAX_INFLUENCE = 4;

]]


VertexShader =
{
	MainCode VertexPdxMeshStandard
	[[
		
		VS_OUTPUT_PDXMESHSTANDARD main( const VS_INPUT_PDXMESHSTANDARD v )
		{
		  	VS_OUTPUT_PDXMESHSTANDARD Out;
					
			float4 vPosition = float4( v.vPosition.xyz, 1.0f );
			Out.vNormal = normalize( mul( CastTo3x3( WorldMatrix ), v.vNormal ) );
			Out.vTangent = normalize( mul( CastTo3x3( WorldMatrix ), v.vTangent.xyz ) );
			Out.vBitangent = normalize( cross( Out.vNormal, Out.vTangent ) * v.vTangent.w );
		
			Out.vPosition = mul( WorldMatrix, vPosition );
			Out.vPos_Height.xyz = Out.vPosition.xyz;
			Out.vPos_Height.w = v.vPosition.y;
			Out.vPos_Height /= WorldMatrix[3][3];
			Out.vPosition = mul( ViewProjectionMatrix, Out.vPosition );
			
			Out.vUV0 = v.vUV0;
#ifdef PDX_MESH_UV1
			Out.vUV1 = v.vUV1;
#else
			Out.vUV1 = v.vUV0;
#endif
		
			return Out;
		}
	]]

	MainCode VertexPdxMeshStandardSkinned
	[[
		
		VS_OUTPUT_PDXMESHSTANDARD main( const VS_INPUT_PDXMESHSTANDARD_SKINNED v )
		{
		  	VS_OUTPUT_PDXMESHSTANDARD Out;
					
			float4 vPosition = float4( v.vPosition.xyz, 1.0 );
			float4 vSkinnedPosition = float4( 0, 0, 0, 0 );
			float3 vSkinnedNormal = float3( 0, 0, 0 );
			float3 vSkinnedTangent = float3( 0, 0, 0 );
			float3 vSkinnedBitangent = float3( 0, 0, 0 );
		
			float4 vWeight = float4( v.vBoneWeight.xyz, 1.0f - v.vBoneWeight.x - v.vBoneWeight.y - v.vBoneWeight.z );
		
			for( int i = 0; i < PDXMESH_MAX_INFLUENCE; ++i )
		    {
				int nIndex = int( v.vBoneIndex[i] );
				float4x4 mat = matBones[nIndex];
				vSkinnedPosition += mul( mat, vPosition ) * vWeight[i];
		
				float3 vNormal = mul( CastTo3x3(mat), v.vNormal );
				float3 vTangent = mul( CastTo3x3(mat), v.vTangent.xyz );
				float3 vBitangent = cross( vNormal, vTangent ) * v.vTangent.w;
		
				vSkinnedNormal += vNormal * vWeight[i];
				vSkinnedTangent += vTangent * vWeight[i];
				vSkinnedBitangent += vBitangent * vWeight[i];
			}
		
			Out.vPosition = mul( WorldMatrix, vSkinnedPosition );
			Out.vPos_Height.xyz = Out.vPosition.xyz;
			Out.vPos_Height.w = vSkinnedPosition.y;
			Out.vPos_Height /= WorldMatrix[3][3];
			Out.vPosition = mul( ViewProjectionMatrix, Out.vPosition );
		
			Out.vNormal = normalize( mul( CastTo3x3(WorldMatrix), normalize( vSkinnedNormal ) ) );
			Out.vTangent = normalize( mul( CastTo3x3(WorldMatrix), normalize( vSkinnedTangent ) ) );
			Out.vBitangent = normalize( mul( CastTo3x3(WorldMatrix), normalize( vSkinnedBitangent ) ) );
		
			Out.vUV0 = v.vUV0;
#ifdef PDX_MESH_UV1
			Out.vUV1 = v.vUV1;
#else
			Out.vUV1 = v.vUV0;
#endif			
			return Out;
		}
	]]

	MainCode VertexPdxMeshStandardShadow
	[[
		
		VS_OUTPUT_PDXMESHSHADOW main( const VS_INPUT_PDXMESHSTANDARD v )
		{
		  	VS_OUTPUT_PDXMESHSHADOW Out;
			float4 vPosition = float4( v.vPosition.xyz, 1.0 );
			Out.vPosition = mul( WorldMatrix, vPosition );
			Out.vPosition = mul( ViewProjectionMatrix, Out.vPosition );
			Out.vDepthUV0 = float4( Out.vPosition.zw, v.vUV0 );
			return Out;
		}
	]]

	MainCode VertexPdxMeshStandardSkinnedShadow
	[[
	
		VS_OUTPUT_PDXMESHSHADOW main( const VS_INPUT_PDXMESHSTANDARD_SKINNED v )
		{
		  	VS_OUTPUT_PDXMESHSHADOW Out;
					
			float4 vPosition = float4( v.vPosition.xyz, 1.0 );
			float4 vSkinnedPosition = float4( 0, 0, 0, 0 );
		
			float4 vWeight = float4( v.vBoneWeight.xyz, 1.0f - v.vBoneWeight.x - v.vBoneWeight.y - v.vBoneWeight.z );
		
			for( int i = 0; i < PDXMESH_MAX_INFLUENCE; ++i )
		    {
				int nIndex = int( v.vBoneIndex[i] );
				float4x4 mat = matBones[nIndex];
				vSkinnedPosition += mul( mat, vPosition ) * vWeight[i];
			}
		
			Out.vPosition = mul( WorldMatrix, vSkinnedPosition );
			Out.vPosition = mul( ViewProjectionMatrix, Out.vPosition );
			Out.vDepthUV0 = float4( Out.vPosition.zw, v.vUV0 );
			return Out;
		}
	]]

	MainCode VertexDebugNormal
	[[
		
		VS_OUTPUT_DEBUGNORMAL main( const VS_INPUT_DEBUGNORMAL v )
		{
		  	VS_OUTPUT_DEBUGNORMAL Out;
		
			Out.vPosition = mul( WorldMatrix, float4( v.vPosition.xyz, 1.0 ) );
			Out.vPosition.xyz += mul( CastTo3x3(WorldMatrix), v.vNormal ) * v.vOffset * 0.3f;
			Out.vPosition = mul( ViewProjectionMatrix, Out.vPosition );	
		
			Out.vUV0 = v.vUV0;
			Out.vOffset = v.vOffset; 
		
			return Out;
		}
	]]

	MainCode VertexDebugNormalSkinned
	[[
		
		VS_OUTPUT_DEBUGNORMAL main( const VS_INPUT_DEBUGNORMAL_SKINNED v )
		{
		  	VS_OUTPUT_DEBUGNORMAL Out;
					
			float4 vPosition = float4( v.vPosition.xyz, 1.0 );
			float4 vSkinnedPosition = float4( 0, 0, 0, 0 );
			float3 vSkinnedNormal = float3( 0, 0, 0 );
		
			float4 vWeight = float4( v.vBoneWeight.xyz, 1.0f - v.vBoneWeight.x - v.vBoneWeight.y - v.vBoneWeight.z );
		
			for( int i = 0; i < PDXMESH_MAX_INFLUENCE; ++i )
		    {
				int nIndex = int( v.vBoneIndex[i] );
				float4x4 mat = matBones[nIndex];
				vSkinnedPosition += mul( mat, vPosition ) * vWeight[i];	
				vSkinnedNormal += mul( CastTo3x3(mat), v.vNormal ) * vWeight[i];
			}
		
			Out.vPosition = mul( WorldMatrix, vSkinnedPosition );
			vSkinnedNormal = normalize( mul( CastTo3x3(WorldMatrix), vSkinnedNormal ) );
			Out.vPosition.xyz += vSkinnedNormal * v.vOffset * 0.3f * WorldMatrix[ 3 ][ 3 ];
			Out.vPosition = mul( ViewProjectionMatrix, Out.vPosition );	
		
			Out.vUV0 = v.vUV0;
			Out.vOffset = v.vOffset; 
			return Out;
		}
	]]
}

PixelShader =
{

	MainCode PixelPdxMeshStandardLotr
	[[
		float3 ApplySnowMesh( float3 vColor, float3 vPos, inout float3 vNormal, float4 vFoWColor, out float vSnowAlpha )
		{
			float vIsSnow = GetSnow( vFoWColor );
			
			// --- UNIFIED LOTR SNOW LOGIC ---
			// 1. Elevation
			float elevation_factor = smoothstep( 20.0f, 26.0f, vPos.y ); 
			
			// 2. Incline: Snow settles on flat ground. 
			// (Noise omitted. The mesh's normal map will naturally break up the edges!)
			float incline_factor = smoothstep( 0.5f, 0.8f, vNormal.y );
			
			// 3. Base Winter Presence: 20% opacity frost everywhere it is winter
			float base_frost = vIsSnow * 0.2f; 
			
			// 4. Thick Snow: Only applied where elevation and incline allow it. 
			float thick_snow = vIsSnow * max(elevation_factor, incline_factor);
			
			// Combine factors
			float total_snow = saturate( base_frost + thick_snow );
			
			// Camera distance fade (Vanilla mesh behavior)
			float vOpacity = cam_distance( SNOW_CAM_MIN, SNOW_CAM_MAX );
			vOpacity = SNOW_OPACITY_MIN + vOpacity * ( SNOW_OPACITY_MAX - SNOW_OPACITY_MIN );
			
			// Calculate final alpha, retaining the 1.5 multiplier to give the mesh snow proper visual weight
			vSnowAlpha = saturate(total_snow * 1.5f) * vOpacity;
			
			// Apply Color
			vColor = lerp( vColor, SNOW_COLOR, vSnowAlpha );
			
			return vColor;
		}

		void calculate_custom_map_tex_index_local( float2 base_uv, float2 tex_size, float2 texel_size, out float4 IndexU, out float4 IndexV, out float vAllSame )
		{
			// 1. Shift UVs by -0.5 to perfectly align the sampling grid with the vFrac blending grid
			float2 grid_uv = base_uv * tex_size - 0.5f;

			// 2. Snap to the top-left texel center of our 2x2 blending group
			float2 snapped_uv = (floor(grid_uv) + 0.5f) * texel_size;

			// 3. Sample the RED channel at the 4 corners of our 2x2 grid
			float id_00 = tex2D( SpecularMap, snapped_uv ).a;                                     // Top-Left
			float id_10 = tex2D( SpecularMap, snapped_uv + float2(texel_size.x, 0) ).a;           // Top-Right
			float id_01 = tex2D( SpecularMap, snapped_uv + float2(0, texel_size.y) ).a;           // Bottom-Left
			float id_11 = tex2D( SpecularMap, snapped_uv + float2(texel_size.x, texel_size.y) ).a;// Bottom-Right

			// 4. Reconstruct the IDs vector
			// We map them to the float4 channels: w = 00, x = 10, y = 01, z = 11
			float4 IDs = float4(id_10, id_01, id_11, id_00);
			IDs *= 255.0f;

			// 5. Calculate vAllSame manually to skip blending if all 4 corners are identical
			float max_diff = max( max( abs(IDs.x - IDs.w), abs(IDs.y - IDs.w) ), abs(IDs.z - IDs.w) );
			vAllSame = (max_diff < 0.5f) ? 1.0f : 0.0f; 

			// 6. Standard atlas math
			IndexV = trunc( ( IDs + 0.5f ) / MAP_NUM_TILES );
			IndexU = trunc( IDs - ( IndexV * MAP_NUM_TILES ) + 0.5f );
		}

		float4 main( VS_OUTPUT_PDXMESHSTANDARD In ) : PDX_COLOR
		{
			float2 local_tex_size = float2(512.0f, 512.0f);
			float2 local_texel_size = 1.0f / local_tex_size;

			float vAllSame;
			float4 IndexU;
			float4 IndexV;

			// 1. Fetch IDs using LOCAL model UVs and our corrected grid math
			calculate_custom_map_tex_index_local( In.vUV0, local_tex_size, local_texel_size, IndexU, IndexV, vAllSame );

			// 2. Calculate World UVs strictly for tiling
			float2 map_uv = float2( ( ( In.vPos_Height.x+0.5f ) / MAP_SIZE_X ), ( ( In.vPos_Height.z+0.5f-MAP_SIZE_Y ) / -MAP_SIZE_Y ));
			float2 vTileRepeat = map_uv * TERRAIN_TILE_FREQ;
			vTileRepeat.x *= MAP_SIZE_X/MAP_SIZE_Y;

			float lod = clamp( mipmapLevel( vTileRepeat ) - 0.5f, 0.0f, 6.0f );
			float vMipTexels = pow( 2.0f, ATLAS_TEXEL_POW2_EXPONENT - lod );

			// 3. Sample the Base Corner (Top-Left) for BOTH Diffuse and Normal
			float4 diffuse = tex2Dlod( DiffuseMap, sample_terrain( IndexU.w, IndexV.w, vTileRepeat, vMipTexels, lod ) ).rgba;
			float4 normalRaw = tex2Dlod( NormalMap, sample_terrain( IndexU.w, IndexV.w, vTileRepeat, vMipTexels, lod ) );
			float vGlossiness = diffuse.a;

			// 4. Standard Bilinear Blending for Diffuse AND Normal
			if ( vAllSame < 1.0f )
			{
				// Diffuse Corners
				float4 Color10 = tex2Dlod( DiffuseMap, sample_terrain( IndexU.x, IndexV.x, vTileRepeat, vMipTexels, lod ) ).rgba;
				float4 Color01 = tex2Dlod( DiffuseMap, sample_terrain( IndexU.y, IndexV.y, vTileRepeat, vMipTexels, lod ) ).rgba;
				float4 Color11 = tex2Dlod( DiffuseMap, sample_terrain( IndexU.z, IndexV.z, vTileRepeat, vMipTexels, lod ) ).rgba;

				// Normal Corners
				float4 Norm10 = tex2Dlod( NormalMap, sample_terrain( IndexU.x, IndexV.x, vTileRepeat, vMipTexels, lod ) );
				float4 Norm01 = tex2Dlod( NormalMap, sample_terrain( IndexU.y, IndexV.y, vTileRepeat, vMipTexels, lod ) );
				float4 Norm11 = tex2Dlod( NormalMap, sample_terrain( IndexU.z, IndexV.z, vTileRepeat, vMipTexels, lod ) );

				float2 vFrac = frac( In.vUV0 * local_tex_size - 0.5f );

				// Blend Diffuse
				diffuse = lerp(
					lerp( diffuse, Color10, vFrac.x ), 
					lerp( Color01, Color11, vFrac.x ), 
					vFrac.y );
					
				// Blend Normal
				normalRaw = lerp(
					lerp( normalRaw, Norm10, vFrac.x ), 
					lerp( Norm01, Norm11, vFrac.x ), 
					vFrac.y );
			}

			// Process the Blended Normal & Specular ---
			// Extract Specular from the Alpha channel of the normal map
			float vSpec = normalRaw.a;

			// Unpack the terrain detail normal (NOTE: HoI4 swizzles this as .rbg!)
			float3 detail_normal = normalize( normalRaw.rbg - 0.5f );

			// Create the TBN matrix from the mesh's vertex data to wrap the detail normal over the 3D shape
			float3x3 TBN = Create3x3( normalize( In.vTangent ), normalize( In.vBitangent ), normalize( In.vNormal ) );
			float3 vNormal = normalize( mul( detail_normal, TBN ) );

			// --- 5. Terrain Color Tint ---
			float3 TerrainColor = tex2D( SpecularMap, In.vUV0 ).rgb;
			diffuse.rgb = GetOverlay( diffuse.rgb, TerrainColor, COLORMAP_OVERLAY_STRENGTH );

			// --- 6. Snow Application ---
			float3 vPos = In.vPos_Height.xyz;
			float4 vMudSnow = GetMudSnowColor( vPos, SnowMudData );
			float vSnowAlpha = 1.0f - vSpec; // Use the actual specular value for snow alpha

			// Apply the mesh-specific snow function using our new vNormal!
			diffuse.rgb = ApplySnowMesh( diffuse.rgb, vPos, vNormal, vMudSnow, vSnowAlpha );

			// --- 7. Gradient Borders & Secondary Color Mask ---
			float vBloomAlpha = 0.0f;
			gradient_border_apply( diffuse.rgb, vNormal, map_uv, GradientBorderChannel1, GradientBorderChannel2, 1.0f, vGBCamDistOverride_GBOutlineCutoff.zw, vGBCamDistOverride_GBOutlineCutoff.xy, vBloomAlpha );
			secondary_color_mask( diffuse.rgb, vNormal, map_uv, ProvinceSecondaryColorMap, vBloomAlpha );

			// --- 8. Lighting Properties Setup ---
			LightingProperties lightingProperties;
			lightingProperties._WorldSpacePos = vPos;
			lightingProperties._ToCameraDir = normalize(vCamPos - vPos);
			lightingProperties._Normal = vNormal;

			#ifdef PDX_IMPROVED_BLINN_PHONG
				float SpecRemapped = vSpec * vSpec * 0.4f;
				float MetalnessRemapped = 0.0f;
				lightingProperties._Diffuse = MetalnessToDiffuse(MetalnessRemapped, diffuse.rgb);
				lightingProperties._Glossiness = vGlossiness;
				lightingProperties._SpecularColor = MetalnessToSpec(MetalnessRemapped, diffuse.rgb, SpecRemapped);
				lightingProperties._NonLinearGlossiness = GetNonLinearGlossiness(vGlossiness);
			#else
				lightingProperties._Diffuse = diffuse.rgb;
				lightingProperties._Glossiness = vGlossiness;
				lightingProperties._SpecularColor = vec3(vSpec);
				lightingProperties._NonLinearGlossiness = GetNonLinearGlossiness(vGlossiness);
			#endif

			float3 diffuseLight = vec3(0.0);
			float3 specularLight = vec3(0.0);

			// --- 8. Screen Coordinates & Shadows ---
			// Translate our 3D world position into 2D clip-space monitor coordinates
			float4 clipSpacePos = mul( ViewProjectionMatrix, float4(vPos, 1.0f) );
			float4 vScreenCoord;

			// Convert to UV space (0.0 to 1.0)
			vScreenCoord.x = ( clipSpacePos.x * 0.5f + clipSpacePos.w * 0.5f );
			vScreenCoord.y = ( clipSpacePos.w * 0.5f - clipSpacePos.y * 0.5f );

			#ifdef PDX_OPENGL
				vScreenCoord.y = -vScreenCoord.y;
			#endif

			vScreenCoord.z = clipSpacePos.w;
			vScreenCoord.w = clipSpacePos.w;

			// We dont have access to ShadowMap, so we just set this to 1.0 (it works)
			//fShadowTerm = max(GetShadowScaled( SHADOW_WEIGHT_TERRAIN, vScreenCoord, ShadowMap ), 0.1f );
			float fShadowTerm = 1.0f;

			// --- 9. Light Calculation ---
			CalculateSunLight( lightingProperties, fShadowTerm, diffuseLight, specularLight );

			#ifdef PDX_IMPROVED_BLINN_PHONG
				CalculatePointLights( lightingProperties, LightDataMap, LightIndexMap, diffuseLight, specularLight);
			#endif

			#ifdef PDX_IMPROVED_BLINN_PHONG
				float3 vEyeDir = normalize( vPos - vCamPos.xyz );
				float3 reflectiveColor = FAKE_CUBEMAP_COLOR; 
				specularLight += reflectiveColor * FresnelGlossy(lightingProperties._SpecularColor, -vEyeDir, lightingProperties._Normal, lightingProperties._Glossiness);
			#endif

			float3 vOut = ComposeLightSnow(lightingProperties, diffuseLight, specularLight, vSnowAlpha);

			// Smoothly remove lighting/shadows near country borders so the colors pop
			vOut = lerp( vOut, diffuse.rgb, BORDER_LIGHT_REMOVAL_FACTOR * ( 1 - vBloomAlpha ) );

			// --- 10. Global Map Effects (Day/Night & Fog of War) ---
			float3 vGlobeNormal = CalcGlobeNormal( vPos.xz );
			float vNightFactor = DayNightFactor( vGlobeNormal );

			// We don't have access to ShadowMap, so FOW is not shown for this object.
			//float3 vFOW = ApplyFOW( vOut, ShadowMap, vScreenCoord );
			//vOut = lerp( vFOW, vOut, BORDER_FOW_REMOVAL_FACTOR * ( 1 - vBloomAlpha ) );

			#ifdef PDX_IMPROVED_BLINN_PHONG
				vOut = ApplyDistanceFog( vOut, vPos );
			#endif

			vOut = DayNightWithBlend( vOut, vGlobeNormal, lerp(BORDER_NIGHT_DESATURATION_MAX, 1.0f, vBloomAlpha) );

			// --- 11. Final Alpha & Fades ---
			float final_alpha = 1.0f;

			// 1. Long Distance Fade (Paper Map Transition)
			// Applies to ALL mountains using this shader so they don't obstruct the paper map
			float far_fade = 1.0f - smoothstep(500.0f, 750.0f, vCamPos.y);
			final_alpha *= far_fade;

			#ifdef LOTR_UNDERGROUND_MOUNTAIN
				float2 ndc_pos = clipSpacePos.xy / clipSpacePos.w;
				ndc_pos.y *= 0.6f;

				// Calculate distance from screen center. 
				float dist_from_center = length(ndc_pos);

				// Camera height factor: 0.0 when zoomed in (<100), 1.0 when zoomed out (>200)
				float height_factor = smoothstep(65.0f, 200.0f, vCamPos.y);
				height_factor = sqrt(height_factor);

				// --- 1. CONTROL THE SIZE OF THE HOLE ---
				float max_hole_radius = 1.5f; 
				float hole_radius = lerp(max_hole_radius, 0.0f, height_factor);

				// --- 2. SMOOTH TRANSITION FOR ALPHA AND COLOR ---
				// You might want to slightly increase thickness since a gradient 
				// takes up more visual space than a hard line to be noticeable.
				float outline_thickness = 0.1f; 

				// smoothstep returns 0.0 when dist <= hole_radius (completely inside the hole)
				// returns 1.0 when dist >= hole_radius + thickness (completely outside)
				// interpolates smoothly between 0.0 and 1.0 across the outline thickness.
				float transition_factor = smoothstep(hole_radius, hole_radius + outline_thickness, dist_from_center);

				// Prevent a blurry dark dot from rendering in the center when fully zoomed out.
				// As the hole_radius approaches 0, we force the transition_factor to 1.0 (normal color/alpha).
				float hole_visibility = smoothstep(0.0f, 0.05f, hole_radius);
				transition_factor = lerp(1.0f, transition_factor, hole_visibility);

				// --- 3. APPLY TO OUTPUT ---
				// Fade alpha to 0.0 (transparent) as it approaches the hole edge.
				final_alpha *= transition_factor;

				// Fade color to 0.0 (black) as it approaches the hole edge.
				// Multiplying by transition_factor is mathematically equivalent to lerp(float3(0,0,0), vOut.rgb, transition_factor).
				vOut.rgb *= transition_factor;
			#endif

			return float4(vOut, final_alpha);
		}
	]]

	MainCode PixelPdxMeshStandard
	[[
		float3 ApplySnowMesh( float3 vColor, float3 vPos, inout float3 vNormal, float4 vFoWColor, out float vSnowAlpha )
		{
			float vIsSnow = GetSnow( vFoWColor );
			float vSnowFade = saturate( saturate( vNormal.y - saturate( 1.0f - vIsSnow ) )*vIsSnow*5.5f*saturate( ( vNormal.y - 0.5f ) * 1000.0f ) );
						
			float vOpacity = cam_distance( SNOW_CAM_MIN, SNOW_CAM_MAX );
			vOpacity = SNOW_OPACITY_MIN + vOpacity * ( SNOW_OPACITY_MAX - SNOW_OPACITY_MIN );
			
			vColor = lerp( vColor, SNOW_COLOR, vSnowFade * vOpacity );
			vSnowAlpha = saturate( vIsSnow * 1.5f ) * vOpacity;
			
			//vNormal.y += 0.5f * vSnowFade;
			//vNormal = normalize( vNormal );
			
			return vColor;
		}

		float4 main( VS_OUTPUT_PDXMESHSTANDARD In ) : PDX_COLOR
		{
			float2 vUV0 = In.vUV0;

		#ifdef UV_ANIM
			const float SPEED_SCALE = 2.0f;
			float t = frac(vGlobalTime * vUVAnimSpeed * SPEED_SCALE);
			vUV0.y += t;
		#endif
		
		#ifdef ATLAS
			float4 vDiffuse = tex2D( DiffuseMap, (vUV0 + AtlasCoordinate.xy) / AtlasCoordinate.zw );
		#else
			float4 vDiffuse = tex2D( DiffuseMap, vUV0 );
		#endif	
		
		//LOTR MOD RELATED CHANGES RIGHT HERE:
		float3 lava_emit = float3(0.0f, 0.0f, 0.0f);
		float lava = 0.0f;
		if(vDiffuse.r>=1.0f && vDiffuse.g<=0.0f && vDiffuse.b>=1.0f) {
			lava = 1.0f;
			lava_emit = tex2D( DiffuseMap, float2(vUV0.x, 1.0f-vUV0.y) ).rgb;
			vDiffuse = float4(1.0f, 1.0f, 1.0f, 1.0f);
		}

		#ifdef ALPHA_TEST
			clip(vDiffuse.a - 1.0);
		#endif
		
			float3 vPos = In.vPos_Height.xyz;
		
			float3 vColor = vDiffuse.rgb;
			float3 vInNormal = normalize( In.vNormal );
			float4 vProperties = tex2D( SpecularMap, vUV0 );
			
			LightingProperties lightingProperties;
			
		#ifdef PDX_IMPROVED_BLINN_PHONG
			float4 vNormalMap = tex2D( NormalMap, vUV0 );
			
			#ifdef EMISSIVE
				float vEmissive = vNormalMap.b;
			#endif
			float3 vNormalSample =  UnpackRRxGNormal(vNormalMap);
			
			lightingProperties._Glossiness = vProperties.a;
		#else
			#ifdef EMISSIVE
				float vEmissive = vProperties.b;
			#endif
			float3 vNormalSample = UnpackNormal( NormalMap, vUV0 );
			
			lightingProperties._SpecularColor = vec3(vProperties.a);
			#ifdef GLOSSINESS
				lightingProperties._Glossiness = vProperties.g * 2048.0 * vProperties.g + 0.00001; // Small epsilon to avoid 0^0
			#else
				lightingProperties._Glossiness = SPECULAR_WIDTH;
			#endif
		#endif
		
			lightingProperties._NonLinearGlossiness = GetNonLinearGlossiness(lightingProperties._Glossiness);
		
			float3x3 TBN = Create3x3( normalize( In.vTangent ), normalize( In.vBitangent ), vInNormal );
			float3 vNormal = normalize(mul( vNormalSample, TBN ));
			
			// self shadowing
			float fShadowTerm = 1.0f;//CalculateShadowCascaded(vPos, ShadowMap);
			//fShadowTerm = (1.0f - SHADOW_WEIGHT_MESH) + SHADOW_WEIGHT_MESH * fShadowTerm;

			float vSnowAlpha = 0;
		#ifdef PDX_SNOW
			float4 vFoWColor = GetMudSnowColor( vPos, SnowMudData );
			vColor = ApplySnowMesh( vColor, vPos, vNormal, vFoWColor, vSnowAlpha );	
		#endif

		#ifdef PDX_GRADIENT_BORDERS
			// Gradient Borders
			float2 map_uv = float2( ( ( vPos.x+0.5f ) / MAP_SIZE_X ), ( ( vPos.z+0.5f-MAP_SIZE_Y ) / -MAP_SIZE_Y ));
			
			float vBloomAlpha = 0.0f;
			gradient_border_apply( vColor.rgb, vNormal, map_uv, GradientBorderChannel1, GradientBorderChannel2, 1.0f, vGBCamDistOverride_GBOutlineCutoff.zw, vGBCamDistOverride_GBOutlineCutoff.xy, vBloomAlpha );

			// Secondary color mask
			secondary_color_mask( vColor.rgb, vNormal, map_uv, ProvinceSecondaryColorMap, vBloomAlpha );	
		#endif
		
			lightingProperties._WorldSpacePos = vPos;
			lightingProperties._ToCameraDir = normalize(vCamPos - vPos);
			lightingProperties._Normal = vNormal;

		#ifdef PDX_IMPROVED_BLINN_PHONG
			float SpecRemapped = vProperties.g * vProperties.g * 0.4;
			float MetalnessRemapped = 1.0 - (1.0 - vProperties.b) * (1.0 - vProperties.b);
			lightingProperties._Diffuse = MetalnessToDiffuse(MetalnessRemapped, vColor);
			lightingProperties._SpecularColor = MetalnessToSpec(MetalnessRemapped, vColor, SpecRemapped);
		#else
			lightingProperties._Diffuse = vColor;
		#endif
			
			float3 diffuseLight = vec3(0.0);
			float3 specularLight = vec3(0.0);
			CalculateSunLight(lightingProperties, fShadowTerm, diffuseLight, specularLight);
			CalculatePointLights(lightingProperties, LightDataMap, LightIndexMap, diffuseLight, specularLight);
		
		#ifdef PDX_IMPROVED_BLINN_PHONG
			float3 vEyeDir = normalize( vPos - vCamPos.xyz );
			float3 reflection = reflect( vEyeDir, vNormal );
			float MipmapIndex = GetEnvmapMipLevel(lightingProperties._Glossiness); 
			
			float3 reflectiveColor = texCUBElod( EnvironmentMap, float4(reflection, MipmapIndex) ).rgb * CubemapIntensity;
			specularLight += reflectiveColor * FresnelGlossy(lightingProperties._SpecularColor, -vEyeDir, lightingProperties._Normal, lightingProperties._Glossiness);
		#endif
		
		#ifdef PDX_SNOW
			vColor = ComposeLightSnow(lightingProperties, diffuseLight, specularLight, vSnowAlpha);
		#else
			vColor = ComposeLightMesh(lightingProperties, diffuseLight, specularLight, vSnowAlpha);
		#endif

			float3 vGlobalNormal = CalcGlobeNormal( vPos.xz );

			float alpha = 0.0f;
		#ifdef EMISSIVE
			float vDayNightFactor = DayNightFactor( vGlobalNormal );
			vEmissive = vEmissive * vDayNightFactor;
			//vColor = lerp( vColor, float3(1,0.7,0), vEmissive * vDayNightFactor );	
			vColor = lerp( vColor, vDiffuse.rgb, vEmissive );
			alpha = vEmissive;
		#endif

			// LOTR STUFF
			if(lava>0.0f) {
				// This controls the "glowiness" of the lava
				lava_emit.rg *= 3.5f;
				// 0.05 controls the amount of black slag on top of the lava, while 1.2 controls how red it is.
				vColor = smoothstep(0, vColor.r, 0.05f) * pow(lava_emit, float3(1.2f, 1.2f, 1.2f));
			}
		
			float FogColorFactor = 0.0;
			float FogAlphaFactor = 0.0;
			GetFogFactors( FogColorFactor, FogAlphaFactor, vPos, 0.0 /*In.vPos_Height.w * 1.0 + 2.5*/, FOWNoise, FOWHeight, IntelMap);
			vColor = ApplyFOW( vColor, FogColorFactor, min( FogAlphaFactor, NegFogMultiplier ) );

			vColor.rgb = ApplyDistanceFog( vColor.rgb, vPos );			
			vColor.rgb = DayNight( vColor.rgb, vGlobalNormal );

/*		#ifdef RIM_LIGHT
			float vRim = smoothstep( RIM_START, RIM_END, 1.0f - dot( vInNormal, lightingProperties._ToCameraDir ) );
			vColor.rgb = lerp( vColor.rgb, RIM_COLOR.rgb, vRim );
		#endif	
*/			

			DebugReturn(vColor, lightingProperties, fShadowTerm);
			
		#ifdef TRAIN
			alpha = TrainColor.a;
			vColor *= TrainColor.rgb;
			float2 toPos = vPos.xz - TrainAlphaStart;
			float cosPos2d = dot( normalize( toPos ), TrainAlphaDir );
			float clipalpha = step( 0.0f, cosPos2d );
			float smoothalpha = smoothstep( 0.0f, 2.5f, length( toPos ) );

			alpha *= clipalpha * smoothalpha;

			return float4(vColor, alpha);

		// TRANSLUCENT effect contains FADE_AT_DISTANCE by default, because I say so
		#elif defined(TRANSLUCENT)
			float4 ret = lerp(vDiffuse, float4(vColor, vDiffuse.a), 0.7f);
			ret.a *= 1.0f-smoothstep(200, 400, vCamPos.y);
			return ret;

		#elif defined(FADE_AT_DISTANCE)
			return float4(vColor, 1.0f-smoothstep(200, 400, vCamPos.y));

		#else
			return float4(vColor, max(alpha, MinMeshAlpha));
		#endif
		}
	]]
	
	MainCode PixelPdxMeshBorder
	[[
	
		float4 main( VS_OUTPUT_PDXMESHSTANDARD In ) : PDX_COLOR
		{
			float4 vDiffuse = tex2D( DiffuseMap, In.vUV0 );
			
		#ifdef ALPHA_TEST
			clip(vDiffuse.a - 1.0);
		#endif
			
			float3 vPos = In.vPos_Height.xyz;
		
			float3 vColor = vDiffuse.rgb;
			float4 vProperties = tex2D( SpecularMap, In.vUV0 );
			
			float4 vNormalMap = tex2D( NormalMap, In.vUV0 );
			float3 vNormalSample = UnpackRRxGNormal(vNormalMap);
			
			LightingProperties lightingProperties;
			lightingProperties._Glossiness = vProperties.a;
			lightingProperties._NonLinearGlossiness = GetNonLinearGlossiness(lightingProperties._Glossiness);
		
			float3 vInNormal = normalize( In.vNormal );
			float3x3 TBN = Create3x3( normalize( In.vTangent ), normalize( In.vBitangent ), vInNormal );
			float3 vNormal = normalize( mul( vNormalSample, TBN ) );

			lightingProperties._WorldSpacePos = vPos;
			lightingProperties._ToCameraDir = normalize(vCamPos - vPos);
			lightingProperties._Normal = vNormal;

			float SpecRemapped = vProperties.g * vProperties.g * 0.4;
			float MetalnessRemapped = 1.0 - (1.0 - vProperties.b) * (1.0 - vProperties.b);
			lightingProperties._Diffuse = MetalnessToDiffuse(MetalnessRemapped, vColor);
			lightingProperties._SpecularColor = MetalnessToSpec(MetalnessRemapped, vColor, SpecRemapped);
			
			float3 diffuseLight = vec3(0.0);
			float3 specularLight = vec3(0.0);
			ImprovedBlinnPhong(BORDER_SUN_INTENSITY, normalize(BORDER_SUN_DIRECTION), lightingProperties, diffuseLight, specularLight);
		
			//float3 vEyeDir = normalize( vPos - vCamPos.xyz );
			//float3 reflection = reflect( vEyeDir, vNormal );
			//float MipmapIndex = GetEnvmapMipLevel(lightingProperties._Glossiness); 
			
			//float3 reflectiveColor = texCUBElod( EnvironmentMap, float4(reflection, MipmapIndex) ).rgb * CubemapIntensity;
			//specularLight += reflectiveColor * FresnelGlossy(lightingProperties._SpecularColor, -vEyeDir, lightingProperties._Normal, lightingProperties._Glossiness);
		
			float3 DayAmbientColors[6];
			DayAmbientColors[0] = AmbientPosX;
			DayAmbientColors[1] = AmbientNegX;
			DayAmbientColors[2] = AmbientPosY;
			DayAmbientColors[3] = AmbientNegY;
			DayAmbientColors[4] = AmbientPosZ;
			DayAmbientColors[5] = AmbientNegZ;
		
			float3 vAmbientColor = AmbientLight(lightingProperties._Normal, 0.0, DayAmbientColors, DayAmbientColors);
			float3 diffuse = ((vAmbientColor + diffuseLight) * lightingProperties._Diffuse) * HdrRange;
			vColor = diffuse + specularLight;

			//vColor.rgb = ApplyDistanceFog( vColor.rgb, vPos );			
			
			return float4( vColor, 0 );
		}
	]]

	MainCode PixelPdxMeshStandardShadow
	[[
			
		float4 main( VS_OUTPUT_PDXMESHSHADOW In ) : PDX_COLOR
		{
			return float4( In.vDepthUV0.xxx / In.vDepthUV0.y, 1.0f );
		}
	]]

	MainCode PixelPdxMeshNoShadow
	[[
			
		float4 main( VS_OUTPUT_PDXMESHSHADOW In ) : PDX_COLOR
		{
			clip( -1.f );
			return float4( 1,1,1,1 );
		}
	]]

	MainCode PixelPdxMeshAlphaBlendShadow
	[[
			
		float4 main( VS_OUTPUT_PDXMESHSHADOW In ) : PDX_COLOR
		{
			float4 vColor = tex2D( DiffuseMap, In.vDepthUV0.zw );
			clip( vColor.a - 0.5f );
			return float4( In.vDepthUV0.xxx / In.vDepthUV0.y, 1.0f );
		}
	]]

	MainCode PixelDebugNormal
	[[
			
		float4 main( VS_OUTPUT_DEBUGNORMAL In ) : PDX_COLOR
		{
			float4 vColor = float4( 1.0f - In.vOffset, In.vOffset, 0.0f,  1.0f );
			return vColor;
		}
	]]
}


BlendState BlendState
{
	BlendEnable = no
	AlphaTest = no
}

BlendState BlendStateAlphaTest
{
	BlendEnable = no
	AlphaTest = yes
}

BlendState BlendStateAlphaTestTrain
{
	BlendEnable = yes
	SourceBlend = "SRC_ALPHA"
	DestBlend = "INV_SRC_ALPHA"
	WriteMask = "RED|GREEN|BLUE"
}

BlendState BlendStateTranslucent
{
	BlendEnable = yes
	SourceBlend = "SRC_ALPHA"
	DestBlend = "INV_SRC_ALPHA"
}

Effect PdxMeshStandard
{
	VertexShader = "VertexPdxMeshStandard"
	PixelShader = "PixelPdxMeshStandard"
}

Effect PdxMeshStandardSkinned
{
	VertexShader = "VertexPdxMeshStandardSkinned"
	PixelShader = "PixelPdxMeshStandard"
}

Effect PdxMeshStandardShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
}

Effect PdxMeshStandardSkinnedShadow
{
	VertexShader = "VertexPdxMeshStandardSkinnedShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
}


Effect PdxMeshStandardSnow
{
	VertexShader = "VertexPdxMeshStandard"
	PixelShader = "PixelPdxMeshStandard"
	Defines = { "PDX_GRADIENT_BORDERS" }
}

Effect PdxMeshStandardSnowShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
}

Effect PdxMeshStandardLotr
{
	VertexShader = "VertexPdxMeshStandard"
	PixelShader = "PixelPdxMeshStandardLotr"
	BlendState = "BlendStateAlphaTestTrain"
	Defines = { "PDX_IMPROVED_BLINN_PHONG" }
}

Effect PdxMeshStandardLotrShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
}

Effect PdxMeshStandardLotrFade
{
	VertexShader = "VertexPdxMeshStandard"
	PixelShader = "PixelPdxMeshStandardLotr"
	BlendState = "BlendStateAlphaTestTrain"
	Defines = { "PDX_IMPROVED_BLINN_PHONG" "LOTR_UNDERGROUND_MOUNTAIN" }
}

Effect PdxMeshStandardLotrFadeShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
}

Effect PdxMeshStandardLotrFadeAmbientObject
{
	VertexShader = "VertexPdxMeshStandard"
	PixelShader = "PixelPdxMeshStandard"
	BlendState = "BlendStateTranslucent"
	Defines = { "EMISSIVE" "PDX_IMPROVED_BLINN_PHONG" "RIM_LIGHT" "PDX_SNOW" "PDX_GRADIENT_BORDERS" "FADE_AT_DISTANCE" }
}

Effect PdxMeshStandardLotrFadeAmbientObjectShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
}


Effect PdxMeshAdvanced
{
	VertexShader = "VertexPdxMeshStandard"
	PixelShader = "PixelPdxMeshStandard"
	Defines = { "EMISSIVE" "PDX_IMPROVED_BLINN_PHONG" "RIM_LIGHT" }
}

Effect PdxMeshAdvancedSkinned
{
	VertexShader = "VertexPdxMeshStandardSkinned"
	PixelShader = "PixelPdxMeshStandard"
	Defines = { "EMISSIVE" "PDX_IMPROVED_BLINN_PHONG" "ATLAS" "RIM_LIGHT"  }
}

Effect PdxMeshAdvancedShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
}

Effect PdxMeshAdvancedSkinnedShadow
{
	VertexShader = "VertexPdxMeshStandardSkinnedShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
}


Effect PdxMeshAdvancedSnow
{
	VertexShader = "VertexPdxMeshStandard"
	PixelShader = "PixelPdxMeshStandard"
	Defines = { "EMISSIVE" "PDX_IMPROVED_BLINN_PHONG" "RIM_LIGHT" "PDX_SNOW" "PDX_GRADIENT_BORDERS" }
}

Effect PdxMeshAdvancedSnowSkinned
{
	VertexShader = "VertexPdxMeshStandardSkinned"
	PixelShader = "PixelPdxMeshStandard"
	Defines = { "EMISSIVE" "PDX_IMPROVED_BLINN_PHONG" "ATLAS" "PDX_SNOW" "RIM_LIGHT"  }
}

Effect PdxMeshAdvancedSnowShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
}

Effect PdxMeshAdvancedSnowSkinnedShadow
{
	VertexShader = "VertexPdxMeshStandardSkinnedShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
}


Effect PdxMeshAdvancedSkinnedAlphaTest
{
	VertexShader = "VertexPdxMeshStandardSkinned"
	PixelShader = "PixelPdxMeshStandard"
	Defines = { "ALPHA_TEST" "ADD_COLOR" "EMISSIVE" "PDX_IMPROVED_BLINN_PHONG" }
}

Effect PdxMeshAdvancedSkinnedAlphaTestShadow
{
	VertexShader = "VertexPdxMeshStandardSkinnedShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
	Defines = { "ALPHA_TEST" }
}


Effect PdxMeshAdvancedAnimSkinned
{
	VertexShader = "VertexPdxMeshStandardSkinned"
	PixelShader = "PixelPdxMeshStandard"
	Defines = { "EMISSIVE" "PDX_IMPROVED_BLINN_PHONG" "UV_ANIM" "RIM_LIGHT" }
}

Effect PdxMeshAdvancedAnimSkinnedShadow
{
	VertexShader = "VertexPdxMeshStandardSkinnedShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
}

Effect PdxMeshTranslucent
{
	VertexShader = "VertexPdxMeshStandard"
	PixelShader = "PixelPdxMeshStandard"
	BlendState = "BlendStateTranslucent"
	Defines = { "TRANSLUCENT" }
}

Effect PdxMeshTranslucentShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshNoShadow"
}

Effect PdxMeshAlphaBlend
{
	VertexShader = "VertexPdxMeshStandard"
	PixelShader = "PixelPdxMeshStandard"
	BlendState = "BlendStateAlphaTest"
}

Effect PdxMeshAlphaBlendSkinned
{
	VertexShader = "VertexPdxMeshStandardSkinned"
	PixelShader = "PixelPdxMeshStandard"
	BlendState = "BlendStateAlphaTest"
}

Effect PdxMeshAlphaBlendShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshAlphaBlendShadow"
}

Effect PdxMeshAlphaBlendSkinnedShadow
{
	VertexShader = "VertexPdxMeshStandardSkinnedShadow"
	PixelShader = "PixelPdxMeshAlphaBlendShadow"
}


Effect PdxMeshSnow
{
	VertexShader = "VertexPdxMeshStandard"
	PixelShader = "PixelPdxMeshStandard"
	Defines = { "PDX_SNOW" "PDX_IMPROVED_BLINN_PHONG" "EMISSIVE" "RIM_LIGHT" "PDX_GRADIENT_BORDERS" }
}

Effect PdxMeshSnowSkinned
{
	VertexShader = "VertexPdxMeshStandardSkinned"
	PixelShader = "PixelPdxMeshStandard"
	Defines = { "PDX_SNOW" }
}

Effect PdxMeshSnowShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
}

Effect PdxMeshSnowSkinnedShadow
{
	VertexShader = "VertexPdxMeshStandardSkinnedShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
}


Effect PdxMeshBorder
{
	VertexShader = "VertexPdxMeshStandard"
	PixelShader = "PixelPdxMeshBorder"
	Defines = { "ALPHA_TEST" }
}

Effect PdxMeshBorderShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshNoShadow"
}


Effect DebugNormal
{
	VertexShader = "VertexDebugNormal"
	PixelShader = "PixelDebugNormal"
}

Effect DebugNormalSkinned
{
	VertexShader = "VertexDebugNormalSkinned"
	PixelShader = "PixelDebugNormal"
}

Effect PdxMeshStandard_NoFoW_NoTISkinned
{
	VertexShader = "VertexPdxMeshStandardSkinned"
	PixelShader = "PixelPdxMeshStandard"
}

Effect PdxMeshStandard_NoFoW_NoTISkinnedShadow
{
	VertexShader = "VertexPdxMeshStandardSkinnedShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
}

Effect PdxMeshTrain
{
	VertexShader = "VertexPdxMeshStandard"
	PixelShader = "PixelPdxMeshStandard"
	BlendState = "BlendStateAlphaTestTrain"
	Defines = { "EMISSIVE" "PDX_IMPROVED_BLINN_PHONG" "RIM_LIGHT" "TRAIN" "ALPHA_TEST" }
}

Effect PdxMeshTrainShadow
{
	VertexShader = "VertexPdxMeshStandardShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
	Defines = { "TRAIN" }
}

Effect PdxMeshTrainSkinned
{
	VertexShader = "VertexPdxMeshStandardSkinned"
	PixelShader = "PixelPdxMeshStandard"
	BlendState = "BlendStateAlphaTestTrain"
	Defines = { "EMISSIVE" "PDX_IMPROVED_BLINN_PHONG" "RIM_LIGHT" "TRAIN" }
}

Effect PdxMeshTrainSkinnedShadow
{
	VertexShader = "VertexPdxMeshStandardSkinnedShadow"
	PixelShader = "PixelPdxMeshStandardShadow"
	Defines = { "TRAIN" }
}