#version 430 core
layout (local_size_x = 1, local_size_y = 1) in;

layout (r32ui, binding = 1) uniform uimage2D outputTexture;

uniform vec2 xbounds;
uniform vec2 ybounds;
uniform uint maxIterations;

void markPoint(vec2 point, vec2 texSize){
    float normX = (point.x - xbounds[0]) / (xbounds[1] - xbounds[0]);
    float normY = (point.y - ybounds[0]) / (ybounds[1] - ybounds[0]);

    ivec2 pixelCoord = ivec2(int(normX * float(texSize.x)), int(normY * float(texSize.y)));

    if (pixelCoord.x >= 0 && pixelCoord.x < texSize.x &&
        pixelCoord.y >= 0 && pixelCoord.y < texSize.y){
        imageAtomicAdd(outputTexture, pixelCoord, 1u);
    }
}

vec2 mul(vec2 a, vec2 b){
  return vec2(a.x*b.x-a.y*b.y, a.x*b.y+a.y*b.x);
}

float random(uint state){
    state ^= 2747636419u;
    state *= 2654435769u;
    state ^= state >> 16;
    state *= 2654435769u;
    state ^= state >> 16;
    state *= 2654435769u;
    return state / 4294967295.0;
}

void main() {
    float xLength = xbounds[1] - xbounds[0];
    float yLength = ybounds[1] - ybounds[0];

    for(int i=0; i<1; i++){
        float seedX = random(gl_GlobalInvocationID.x + i);
        float seedY = random(gl_GlobalInvocationID.y + i);
        vec2 samplePoint = vec2(seedX * xLength + xbounds[0] , seedY * yLength + ybounds[0]);

        ivec2 texSize = imageSize(outputTexture);

        vec2 z = vec2(0.0, 0.0);
        bool escaped = false;
        uint escapeCount = 0;

        for(uint i=0; i<maxIterations; i++){
            z = mul(z, z) + samplePoint;
            if (length(z) > 2.0) {
                escaped = true;
                escapeCount = i + 1;
                break;
            }
        }

        if (escaped) {
            z = vec2(0.0, 0.0);
            for (uint j=0; j<escapeCount; j++){
                z = mul(z, z) + samplePoint;
                markPoint(z, texSize);
            }
        }
    }
}