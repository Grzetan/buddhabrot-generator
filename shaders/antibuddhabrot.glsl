#version 430 core
layout (local_size_x = 32, local_size_y = 32) in;

layout (r32ui, binding = 1) uniform uimage2D outputTexture;

uniform vec2 xbounds;
uniform vec2 ybounds;
uniform vec2 origC; // Leave this uniform unused to ensure compatibility with buddha julia sets
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

vec2 power(vec2 z, vec2 w) {
  float r = length(z);
  float theta = atan(z.y, z.x);

  float r_ = pow(r, w.x);
  float theta_ = theta * w.x;

  if (w.y != 0.0) {
    r_ *= exp(-w.y*theta);
    theta_ += w.y*log(r);
  }

  return vec2(r_*cos(theta_), r_*sin(theta_));
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

vec2 conjugate(vec2 z) {
    return vec2(z.x, -z.y);
}

float abs(float a) {
    if(a >= 0.0){
        return a;
    }
    return -a;
}

vec2 cabs(vec2 z){
  return vec2(abs(z.x), abs(z.y));
}

void main() {
    float xLength = xbounds[1] - xbounds[0];
    float yLength = ybounds[1] - ybounds[0];

    uint iterationCount = 16000;
    uint numberBase = max(iterationCount, gl_NumWorkGroups.x * gl_WorkGroupSize.x) + 1;

    for(uint i=0; i<iterationCount; i++){
        float seedX = random(i * numberBase * numberBase + gl_GlobalInvocationID.x * numberBase + gl_GlobalInvocationID.y);
        float seedY = random(i * numberBase * numberBase + gl_GlobalInvocationID.y * numberBase + gl_GlobalInvocationID.x);
        ivec2 texSize = imageSize(outputTexture);

        vec2 c = vec2(seedX * xLength + xbounds[0] , seedY * yLength + ybounds[0]);
        vec2 origZ = vec2(0.0, 0.0);

        bool escaped = false;
        uint escapeCount = 0;

        vec2 z = origZ;
        for(uint i=0; i<maxIterations; i++){
            z = power(z, vec2(2, 0.0)) + c;
            // Tricorn: z = power(conjugate(z), vec2(2, 0.0)) + c;
            // BurningShip: z = power(cabs(z), vec2(2, 0.0)) + c;
            if (length(z) > 2.0) {
                escaped = true;
                escapeCount = i + 1;
                break;
            }
        }

        if (!escaped) {
            z = origZ;
            for (uint j=0; j<maxIterations; j++){
                z = power(z, vec2(2, 0.0)) + c;
                // Tricorn: z = power(conjugate(z), vec2(2, 0.0)) + c;
                // BurningShip: z = power(cabs(z), vec2(2, 0.0)) + c;
                markPoint(z, texSize);
            }
        }
    }
}