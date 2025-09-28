"""
Video and Image Generation Client
A client for generating videos with Veo 3 and images with Imagen models
"""

import os
import time
import mimetypes
from typing import Optional, Dict, Any, Union, List
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv


class VideoImageClient:
    """Client for video generation with Veo 3 and image generation with Imagen"""
    
    def __init__(self):
        """Initialize the video/image generation client"""
        # Load environment variables
        load_dotenv()
        
        # Get API key from environment
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        # Validate API key
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please copy .env.example to .env and add your API key."
            )
        
        # Initialize the client
        try:
            self.client = genai.Client(api_key=self.api_key)
            print("✅ Successfully initialized Video/Image generation client")
        except Exception as e:
            raise ValueError(f"Failed to initialize client: {str(e)}")
    
    def generate_image(self, prompt: str, output_path: Optional[str] = None) -> str:
        """
        Generate an image using Imagen model
        
        Args:
            prompt (str): The text prompt for image generation
            output_path (str, optional): Path to save the generated image
            
        Returns:
            str: Path to the saved image file
        """
        try:
            print(f"🎨 Generating image with prompt: '{prompt}'")
            
            # Generate image with Imagen
            imagen_response = self.client.models.generate_images(
                model="imagen-4.0-generate-001",
                prompt=prompt,
            )
            
            # Set default output path if not provided
            if not output_path:
                timestamp = int(time.time())
                output_path = f"generated_image_{timestamp}.png"
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save the generated image
            # The response contains generated_images array
            if hasattr(imagen_response, 'generated_images') and imagen_response.generated_images:
                generated_image = imagen_response.generated_images[0]
                generated_image.image.save(output_path)
            else:
                raise RuntimeError("No generated images found in API response")
            
            print(f"✅ Image saved to: {output_path}")
            return output_path
            
        except Exception as e:
            error_msg = str(e)
            if "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                raise RuntimeError(f"Image generation quota exceeded. Please check your billing and rate limits: {error_msg}")
            elif "429" in error_msg:
                raise RuntimeError(f"Rate limit exceeded. Please wait before trying again: {error_msg}")
            else:
                raise RuntimeError(f"Error generating image: {error_msg}")
    
    def generate_video_from_prompt(self, prompt: str, output_path: Optional[str] = None) -> str:
        """
        Generate a video using Veo 3 model from text prompt only
        
        Args:
            prompt (str): The text prompt for video generation
            output_path (str, optional): Path to save the generated video
            
        Returns:
            str: Path to the saved video file
        """
        try:
            print(f"🎬 Generating video with prompt: '{prompt}'")
            
            # Generate video with Veo 3
            operation = self.client.models.generate_videos(
                model="veo-3.0-generate-001",
                prompt=prompt,
            )
            
            # Poll the operation status until the video is ready
            print("⏳ Waiting for video generation to complete...")
            while not operation.done:
                print("   Still processing...")
                time.sleep(10)
                operation = self.client.operations.get(operation)
            
            # Set default output path if not provided
            if not output_path:
                timestamp = int(time.time())
                output_path = f"generated_video_{timestamp}.mp4"
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Download the generated video
            generated_video = operation.response.generated_videos[0]
            self.client.files.download(file=generated_video.video)
            generated_video.video.save(output_path)
            
            print(f"✅ Video saved to: {output_path}")
            return output_path
            
        except Exception as e:
            error_msg = str(e)
            if "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                raise RuntimeError(f"Video generation quota exceeded. Please check your billing and rate limits: {error_msg}")
            elif "429" in error_msg:
                raise RuntimeError(f"Rate limit exceeded. Please wait before trying again: {error_msg}")
            else:
                raise RuntimeError(f"Error generating video: {error_msg}")
    
    def generate_video_from_image(self, prompt: str, image_path: str, output_path: Optional[str] = None) -> str:
        """
        Generate a video using Veo 3 model from text prompt and input image
        
        Args:
            prompt (str): The text prompt for video generation
            image_path (str): Path to the input image file
            output_path (str, optional): Path to save the generated video
            
        Returns:
            str: Path to the saved video file
        """
        try:
            print(f"🎬 Generating video with prompt: '{prompt}' and image: '{image_path}'")
            
            # Resolve absolute path and validate image file exists
            image_path = str(Path(image_path).resolve())
            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Read the image file as bytes
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type or not mime_type.startswith('image/'):
                mime_type = 'image/jpeg'  # Default fallback
            
            # Create image object using the correct Image type
            image_obj = types.Image(
                imageBytes=image_data,
                mimeType=mime_type
            )
            
            # Generate video with Veo 3 using the image
            operation = self.client.models.generate_videos(
                model="veo-3.0-generate-001",
                prompt=prompt,
                image=image_obj,
            )
            
            # Poll the operation status until the video is ready
            print("⏳ Waiting for video generation to complete...")
            while not operation.done:
                print("   Still processing...")
                time.sleep(10)
                operation = self.client.operations.get(operation)
            
            # Set default output path if not provided
            if not output_path:
                timestamp = int(time.time())
                output_path = f"generated_video_from_image_{timestamp}.mp4"
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Download the generated video
            generated_video = operation.response.generated_videos[0]
            self.client.files.download(file=generated_video.video)
            generated_video.video.save(output_path)
            
            print(f"✅ Video saved to: {output_path}")
            return output_path
            
        except Exception as e:
            error_msg = str(e)
            if "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                raise RuntimeError(f"Video generation quota exceeded. Please check your billing and rate limits: {error_msg}")
            elif "429" in error_msg:
                raise RuntimeError(f"Rate limit exceeded. Please wait before trying again: {error_msg}")
            else:
                raise RuntimeError(f"Error generating video from image: {error_msg}")
    
    def generate_image_then_video(self, image_prompt: str, video_prompt: Optional[str] = None, 
                                 image_output: Optional[str] = None, video_output: Optional[str] = None) -> Dict[str, str]:
        """
        Generate an image first, then use it to create a video
        
        Args:
            image_prompt (str): Prompt for image generation
            video_prompt (str, optional): Prompt for video generation (uses image_prompt if not provided)
            image_output (str, optional): Path to save the generated image
            video_output (str, optional): Path to save the generated video
            
        Returns:
            Dict[str, str]: Dictionary with 'image' and 'video' file paths
        """
        try:
            print(f"🎨➡️🎬 Generating image then video workflow")
            
            # Step 1: Generate image
            image_path = self.generate_image(image_prompt, image_output)
            
            # Step 2: Generate video using the image
            video_prompt_final = video_prompt or image_prompt
            video_path = self.generate_video_from_image(video_prompt_final, image_path, video_output)
            
            return {
                'image': image_path,
                'video': video_path
            }
            
        except Exception as e:
            raise RuntimeError(f"Error in image-to-video workflow: {str(e)}")
    
    def create_video_with_image_upload(self, image_file_path: str, prompt: str, 
                                      output_path: Optional[str] = None, 
                                      validate_image: bool = True) -> str:
        """
        Create a video by uploading an image file and providing animation prompt
        
        Args:
            image_file_path (str): Path to the image file to upload
            prompt (str): Text prompt describing how to animate the image
            output_path (str, optional): Path to save the generated video
            validate_image (bool): Whether to validate image file before upload
            
        Returns:
            str: Path to the saved video file
        """
        try:
            print(f"🖼️ Processing image upload: '{image_file_path}'")
            print(f"🎬 Animation prompt: '{prompt}'")
            
            # Validate image file if requested
            if validate_image:
                if not Path(image_file_path).exists():
                    raise FileNotFoundError(f"Image file not found: {image_file_path}")
                
                # Check file extension
                valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
                file_extension = Path(image_file_path).suffix.lower()
                if file_extension not in valid_extensions:
                    raise ValueError(f"Unsupported image format: {file_extension}. Supported: {valid_extensions}")
                
                # Check file size (optional - you can adjust this limit)
                file_size = Path(image_file_path).stat().st_size
                max_size = 50 * 1024 * 1024  # 50MB limit
                if file_size > max_size:
                    raise ValueError(f"Image file too large: {file_size / (1024*1024):.1f}MB. Max: {max_size / (1024*1024)}MB")
                
                print(f"✅ Image validation passed: {file_extension}, {file_size / (1024*1024):.1f}MB")
            
            # Use the existing generate_video_from_image method
            return self.generate_video_from_image(prompt, image_file_path, output_path)
            
        except Exception as e:
            raise RuntimeError(f"Error creating video with image upload: {str(e)}")
    
    def analyze_image_content(self, image_path: str, gemini_client=None) -> str:
        """
        Analyze image content to extract attributes and description using Gemini API
        
        Args:
            image_path (str): Path to the image file
            gemini_client: GeminiClient instance for image analysis
            
        Returns:
            str: Description of image content and attributes
        """
        try:
            # Resolve absolute path
            image_path = str(Path(image_path).resolve())
            print(f"🔍 Analyzing image content: '{image_path}'")
            
            if not gemini_client:
                print("⚠️ No Gemini client provided for image analysis")
                return f"Image showing visual content from {Path(image_path).name}"
            
            # Validate image file exists
            if not Path(image_path).exists():
                print(f"⚠️ Image file not found: {image_path}")
                return f"Image showing visual content from {Path(image_path).name} - File not found"
            
            # Create analysis prompt for image understanding
            analysis_prompt = """Analyze this image in detail and provide:

1. **Main Subjects & Objects**: What are the primary elements in the image?
2. **Setting & Location**: Indoor/outdoor, architectural style, environment type
3. **Mood & Atmosphere**: What feeling or emotion does the image convey?
4. **Visual Style**: Colors, lighting, composition, artistic elements
5. **Spatial Elements**: Depth, perspective, layout, focal points
6. **Video Potential**: How could this be animated? What camera movements would work?
7. **Narrative Elements**: What story could this image tell in motion?

Provide a comprehensive analysis that would help create an immersive video experience. Focus on elements that could inspire dynamic video content."""

            # Use Gemini API to analyze the image
            print("🤖 Using Gemini API for image analysis...")
            
            # Convert image to base64 for Gemini API
            import base64
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type or not mime_type.startswith('image/'):
                mime_type = 'image/jpeg'
            
            # Create the message with image for Gemini API
            analysis = gemini_client.analyze_image(
                image_base64=image_base64,
                mime_type=mime_type,
                prompt=analysis_prompt
            )
            
            print(f"✅ Image analysis complete ({len(analysis)} characters)")
            return analysis
            
        except Exception as e:
            print(f"⚠️ Error analyzing image: {str(e)}")
            return f"Image showing visual content from {Path(image_path).name} - Analysis failed: {str(e)}"

    def create_immersive_video_from_images(self, image_paths: List[str], user_prompt: str, 
                                         output_path: Optional[str] = None, gemini_client=None) -> str:
        """
        Create a single immersive video by analyzing multiple images and combining with user prompt
        
        Args:
            image_paths (List[str]): List of paths to image files
            user_prompt (str): User's prompt for the video experience
            output_path (str, optional): Path to save the generated video
            
        Returns:
            str: Path to the saved video file
        """
        try:
            print(f"🎬 Creating immersive video from {len(image_paths)} images")
            print(f"🎯 User prompt: '{user_prompt}'")
            
            # Step 1: Analyze all images using Gemini API
            image_analyses = []
            for i, image_path in enumerate(image_paths, 1):
                print(f"📸 Analyzing image {i}/{len(image_paths)} with Gemini API")
                analysis = self.analyze_image_content(image_path, gemini_client)
                image_analyses.append({
                    'path': image_path,
                    'analysis': analysis
                })
            
            # Step 2: Create comprehensive prompt combining all analyses
            combined_analysis = "\n\n".join([
                f"Image {i+1}: {analysis['analysis']}" 
                for i, analysis in enumerate(image_analyses)
            ])
            
            # Step 3: Generate enhanced prompt for video creation
            enhanced_prompt = f"""Create an immersive video experience that combines elements from multiple source images with the user's vision.

USER REQUEST: {user_prompt}

SOURCE IMAGES ANALYSIS:
{combined_analysis}

INSTRUCTIONS:
- Create a cohesive narrative that weaves together visual elements from all source images
- Maintain the style and atmosphere suggested by the user prompt
- Use smooth transitions and camera movements to create an immersive experience
- Blend architectural, environmental, and atmospheric elements from the analyzed images
- Focus on creating a single, unified video that tells a complete story
- Emphasize the immersive quality requested by the user"""

            print(f"🎨 Enhanced prompt created ({len(enhanced_prompt)} characters)")
            
            # Step 4: Use the first image as the primary reference for video generation
            primary_image_path = image_paths[0]
            
            # Step 5: Generate the immersive video
            print("🎬 Generating immersive video...")
            video_path = self.generate_video_from_image(
                prompt=enhanced_prompt,
                image_path=primary_image_path,
                output_path=output_path
            )
            
            print(f"✅ Immersive video created: {video_path}")
            return video_path
            
        except Exception as e:
            raise RuntimeError(f"Error creating immersive video: {str(e)}")

    def batch_create_videos_from_images(self, image_prompt_pairs: List[Dict[str, str]], 
                                       output_dir: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Create multiple videos from a list of image-prompt pairs
        
        Args:
            image_prompt_pairs (List[Dict]): List of dicts with 'image_path' and 'prompt' keys
            output_dir (str, optional): Directory to save all generated videos
            
        Returns:
            List[Dict]: List of results with image_path, prompt, video_path, and status
        """
        try:
            print(f"🎬 Starting batch video creation for {len(image_prompt_pairs)} items")
            
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            results = []
            
            for i, pair in enumerate(image_prompt_pairs, 1):
                try:
                    image_path = pair.get('image_path')
                    prompt = pair.get('prompt')
                    
                    if not image_path or not prompt:
                        results.append({
                            'image_path': image_path,
                            'prompt': prompt,
                            'video_path': None,
                            'status': 'error',
                            'error': 'Missing image_path or prompt'
                        })
                        continue
                    
                    print(f"\n📹 Processing {i}/{len(image_prompt_pairs)}: {Path(image_path).name}")
                    
                    # Generate output path
                    if output_dir:
                        timestamp = int(time.time())
                        video_filename = f"batch_video_{i}_{timestamp}.mp4"
                        video_output_path = Path(output_dir) / video_filename
                    else:
                        video_output_path = None
                    
                    # Create video
                    video_path = self.create_video_with_image_upload(
                        image_path, prompt, str(video_output_path) if video_output_path else None
                    )
                    
                    results.append({
                        'image_path': image_path,
                        'prompt': prompt,
                        'video_path': video_path,
                        'status': 'success',
                        'error': None
                    })
                    
                    print(f"✅ Completed {i}/{len(image_prompt_pairs)}")
                    
                except Exception as e:
                    print(f"❌ Failed {i}/{len(image_prompt_pairs)}: {str(e)}")
                    results.append({
                        'image_path': pair.get('image_path'),
                        'prompt': pair.get('prompt'),
                        'video_path': None,
                        'status': 'error',
                        'error': str(e)
                    })
            
            successful = len([r for r in results if r['status'] == 'success'])
            print(f"\n🎯 Batch processing complete: {successful}/{len(image_prompt_pairs)} successful")
            
            return results
            
        except Exception as e:
            raise RuntimeError(f"Error in batch video creation: {str(e)}")
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get information about the client configuration"""
        return {
            'api_key_set': bool(self.api_key),
            'supported_models': {
                'video': 'veo-3.0-generate-001',
                'image': 'imagen-4.0-generate-001'
            },
            'supported_image_formats': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'],
            'max_image_size_mb': 50
        }


def main():
    """Main function to demonstrate video and image generation"""
    try:
        # Initialize client
        client = VideoImageClient()
        
        # Display client info
        info = client.get_client_info()
        print(f"\n📋 Client Configuration:")
        print(f"   API Key Set: {info['api_key_set']}")
        print(f"   Video Model: {info['supported_models']['video']}")
        print(f"   Image Model: {info['supported_models']['image']}")
        
        # Display supported formats
        print(f"   Supported Image Formats: {', '.join(info['supported_image_formats'])}")
        print(f"   Max Image Size: {info['max_image_size_mb']}MB")
        
        # Interactive mode
        print(f"\n🎬 Video & Image Generation")
        print("Choose an option:")
        print("1. Generate image only")
        print("2. Generate video from text prompt")
        print("3. 🖼️ Create video with image upload (Enhanced)")
        print("4. Generate image then video (full workflow)")
        print("5. 📹 Batch create videos from multiple images")
        print("Type 'quit' to exit")
        print("=" * 60)
        
        while True:
            try:
                choice = input("\n👤 Your choice (1-5): ").strip()
                
                if choice.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if choice == '1':
                    prompt = input("🎨 Enter image prompt: ").strip()
                    if prompt:
                        client.generate_image(prompt)
                
                elif choice == '2':
                    prompt = input("🎬 Enter video prompt: ").strip()
                    if prompt:
                        client.generate_video_from_prompt(prompt)
                
                elif choice == '3':
                    print("\n🖼️ Create Video with Image Upload")
                    print("This feature validates your image and creates an animated video.")
                    image_path = input("📁 Enter path to image file: ").strip()
                    if not image_path:
                        print("❌ Image path is required")
                        continue
                    
                    prompt = input("🎬 Enter animation prompt (describe how to animate the image): ").strip()
                    if not prompt:
                        print("❌ Animation prompt is required")
                        continue
                    
                    # Ask for validation preference
                    validate = input("🔍 Validate image file? (y/n, default: y): ").strip().lower()
                    validate_image = validate != 'n'
                    
                    try:
                        video_path = client.create_video_with_image_upload(
                            image_path, prompt, validate_image=validate_image
                        )
                        print(f"🎉 Video created successfully: {video_path}")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                
                elif choice == '4':
                    image_prompt = input("🎨 Enter image prompt: ").strip()
                    video_prompt = input("🎬 Enter video prompt (or press Enter to use same): ").strip()
                    if image_prompt:
                        result = client.generate_image_then_video(
                            image_prompt, 
                            video_prompt if video_prompt else None
                        )
                        print(f"✅ Generated: {result}")
                
                elif choice == '5':
                    print("\n📹 Batch Video Creation from Images")
                    print("Create multiple videos from image files.")
                    
                    # Get number of images
                    try:
                        num_images = int(input("📊 How many images do you want to process? "))
                        if num_images <= 0:
                            print("❌ Number must be greater than 0")
                            continue
                    except ValueError:
                        print("❌ Please enter a valid number")
                        continue
                    
                    # Collect image-prompt pairs
                    image_prompt_pairs = []
                    for i in range(num_images):
                        print(f"\n--- Image {i+1}/{num_images} ---")
                        image_path = input(f"📁 Image {i+1} path: ").strip()
                        prompt = input(f"🎬 Animation prompt for image {i+1}: ").strip()
                        
                        if image_path and prompt:
                            image_prompt_pairs.append({
                                'image_path': image_path,
                                'prompt': prompt
                            })
                        else:
                            print(f"⚠️ Skipping image {i+1} (missing path or prompt)")
                    
                    if not image_prompt_pairs:
                        print("❌ No valid image-prompt pairs provided")
                        continue
                    
                    # Ask for output directory
                    output_dir = input("📂 Output directory (press Enter for default): ").strip()
                    if not output_dir:
                        output_dir = "batch_videos"
                    
                    try:
                        results = client.batch_create_videos_from_images(
                            image_prompt_pairs, output_dir
                        )
                        
                        # Display results summary
                        print(f"\n📊 Batch Processing Results:")
                        for i, result in enumerate(results, 1):
                            status_emoji = "✅" if result['status'] == 'success' else "❌"
                            print(f"  {status_emoji} Image {i}: {result['status']}")
                            if result['status'] == 'error':
                                print(f"      Error: {result['error']}")
                            else:
                                print(f"      Video: {result['video_path']}")
                        
                    except Exception as e:
                        print(f"❌ Batch processing error: {e}")
                
                else:
                    print("❌ Invalid choice. Please select 1-5.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                
    except Exception as e:
        print(f"❌ Failed to initialize client: {str(e)}")
        print("\n💡 Make sure to:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Gemini API key to the .env file")
        print("   3. Install requirements: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
