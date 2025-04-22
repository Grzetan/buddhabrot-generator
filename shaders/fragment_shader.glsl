#version 430
in vec2 fragTexCoord;
out vec4 outColor;

uniform usampler2D inputTexture;

void main() {
    uvec4 texel = texture(inputTexture, fragTexCoord);
    uint count = texel.r;

    float intensity;
    intensity = float(count) / 25;
    outColor = vec4(intensity, intensity, intensity, 1.0); 
}