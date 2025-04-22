#version 430
layout (local_size_x = 16, local_size_y = 16) in;

layout (rgba32f, binding = 1) uniform image2D outputTexture;


void main() {
    ivec2 pixelCoord = ivec2(gl_GlobalInvocationID.xy);
    ivec2 texSize = imageSize(outputTexture);

    if (pixelCoord.x >= texSize.x || pixelCoord.y >= texSize.y) {
        return;
    }

    if(pixelCoord.x < 100){
        imageStore(outputTexture, pixelCoord, vec4(1.0, 0.0, 0.0, 1.0));
    }
}