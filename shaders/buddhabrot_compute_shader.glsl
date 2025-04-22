#version 430
layout (local_size_x = 8, local_size_y = 1) in;

layout (std430, binding = 0) buffer SSBO {
    vec2 samples[];
} ssbo;

layout (rgba32f, binding = 1) uniform image2D outputTexture;

uniform uint ssboSize;
uniform vec2 xbounds;
uniform vec2 ybounds;

void main() {
    uint index = gl_GlobalInvocationID.x;

    if (index >= ssboSize) {
        return;
    }

    vec2 samplePos = ssbo.samples[index];
    ivec2 texSize = imageSize(outputTexture);

    float normX = (samplePos.x - xbounds[0]) / (xbounds[1] - xbounds[0]);
    float normY = (samplePos.y - ybounds[0]) / (ybounds[1] - ybounds[0]);

    ivec2 pixelCoord = ivec2(int(normX * float(texSize.x)), int(normY * float(texSize.y)));

    if (pixelCoord.x >= 0 && pixelCoord.x < texSize.x &&
        pixelCoord.y >= 0 && pixelCoord.y < texSize.y){
        imageStore(outputTexture, pixelCoord, vec4(1.0, 0.0, 0.0, 1.0));
    }
}