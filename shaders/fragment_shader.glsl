#version 430
in vec2 fragTexCoord;
out vec4 outColor;

uniform usampler2D inputTexture;
uniform uint textureMaxSize;


void main() {
    uvec4 texel = texture(inputTexture, fragTexCoord);
    uint count = texel.r;

    float intensity;
    intensity = float(count) / float(textureMaxSize);
    outColor = vec4(intensity, intensity, intensity, 1.0); 
}