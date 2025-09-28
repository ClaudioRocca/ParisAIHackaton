"""
Video and Image Generation Examples
Examples demonstrating Veo 3 video generation and Imagen image generation
"""

from video_client import VideoImageClient
import os


def example_dialogue_video():
    """Example: Generate a dialogue video like in the user's request"""
    print("🔹 Dialogue Video Generation Example")
    print("=" * 50)
    
    client = VideoImageClient()
    
    prompt = """A close up of two people staring at a cryptic drawing on a wall, torchlight flickering.
A man murmurs, 'This must be it. That's the secret code.' The woman looks at him and whispering excitedly, 'What did you find?'"""
    
    try:
        video_path = client.generate_video_from_prompt(prompt, "dialogue_example.mp4")
        print(f"✅ Dialogue video generated: {video_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()


def example_image_generation():
    """Example: Generate various types of images"""
    print("🔹 Image Generation Examples")
    print("=" * 40)
    
    client = VideoImageClient()
    
    prompts = [
        "A serene mountain landscape at sunset with a crystal clear lake",
        "A futuristic cityscape with flying cars and neon lights",
        "A cute robot reading a book in a cozy library"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        try:
            print(f"\n🎨 Generating image {i}: {prompt}")
            image_path = client.generate_image(prompt, f"example_image_{i}.png")
            print(f"✅ Image saved: {image_path}")
        except Exception as e:
            print(f"❌ Error generating image {i}: {e}")
    print()


def example_kitten_video():
    """Example: Generate kitten video like in the user's request"""
    print("🔹 Kitten Video with Image Input Example")
    print("=" * 50)
    
    client = VideoImageClient()
    
    prompt = "Panning wide shot of a calico kitten sleeping in the sunshine"
    
    try:
        # Generate image first, then video
        result = client.generate_image_then_video(
            image_prompt=prompt,
            video_prompt=prompt,
            image_output="kitten_image.png",
            video_output="veo3_with_image_input.mp4"
        )
        print(f"✅ Generated kitten content: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()


def example_creative_workflow():
    """Example: Creative workflow from concept to video"""
    print("🔹 Creative Workflow Example")
    print("=" * 40)
    
    client = VideoImageClient()
    
    # Step 1: Create a concept image
    image_prompt = "A magical forest with glowing mushrooms and fairy lights, ethereal atmosphere"
    
    # Step 2: Animate it with a different video prompt
    video_prompt = "Camera slowly pans through the magical forest as fairy lights dance and mushrooms pulse with gentle light"
    
    try:
        result = client.generate_image_then_video(
            image_prompt=image_prompt,
            video_prompt=video_prompt,
            image_output="magical_forest_concept.png",
            video_output="magical_forest_animation.mp4"
        )
        print(f"✅ Creative workflow completed: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()


def example_action_sequence():
    """Example: Generate action sequence video"""
    print("🔹 Action Sequence Video Example")
    print("=" * 40)
    
    client = VideoImageClient()
    
    prompt = """A superhero in a red cape leaps from rooftop to rooftop across a bustling city at night. 
The camera follows the hero's dynamic movement as they soar through the air, city lights blurring below."""
    
    try:
        video_path = client.generate_video_from_prompt(prompt, "superhero_action.mp4")
        print(f"✅ Action sequence generated: {video_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()


def example_nature_documentary():
    """Example: Nature documentary style video"""
    print("🔹 Nature Documentary Example")
    print("=" * 40)
    
    client = VideoImageClient()
    
    # First generate a nature scene image
    image_prompt = "A majestic eagle perched on a rocky cliff overlooking a vast canyon at golden hour"
    
    # Then animate it with documentary-style movement
    video_prompt = "The eagle spreads its wings and takes flight, soaring gracefully over the canyon as the camera follows its majestic flight"
    
    try:
        result = client.generate_image_then_video(
            image_prompt=image_prompt,
            video_prompt=video_prompt,
            image_output="eagle_scene.png",
            video_output="nature_documentary.mp4"
        )
        print(f"✅ Nature documentary created: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()


def example_upload_and_animate():
    """Example: Upload your own image and animate it"""
    print("🔹 Upload and Animate Example")
    print("=" * 40)
    
    client = VideoImageClient()
    
    # This example assumes you have an image file to upload
    image_path = input("📁 Enter path to your image file (or press Enter to skip): ").strip()
    
    if image_path and os.path.exists(image_path):
        video_prompt = input("🎬 Enter how you want to animate this image: ").strip()
        
        if video_prompt:
            try:
                video_path = client.generate_video_from_image(
                    prompt=video_prompt,
                    image_path=image_path,
                    output_path="user_uploaded_animation.mp4"
                )
                print(f"✅ Your image has been animated: {video_path}")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("⚠️ No animation prompt provided")
    else:
        print("⚠️ No valid image file provided, skipping this example")
    print()


def main():
    """Run all video and image generation examples"""
    print("🚀 Video & Image Generation Examples")
    print("=" * 60)
    
    try:
        # Run examples
        example_image_generation()
        example_dialogue_video()
        example_kitten_video()
        example_creative_workflow()
        example_action_sequence()
        example_nature_documentary()
        example_upload_and_animate()
        
        print("✅ All examples completed!")
        print("\n📁 Check your project directory for generated files:")
        print("   - *.png files (generated images)")
        print("   - *.mp4 files (generated videos)")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
        print("\n💡 Make sure your .env file is properly configured")
        print("💡 Video generation requires a valid Gemini API key with access to Veo 3")


if __name__ == "__main__":
    main()
