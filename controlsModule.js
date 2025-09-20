/**
 * Controls Module for Web Bouncer Applications
 * 
 * This reusable module provides complete controls functionality for teleprompter applications.
 * It handles the tape deck controls UI including image loading, button detection, and interactions.
 * 
 * FEATURES:
 * - Automatic controls image loading with fallback to procedural generation
 * - Dynamic button coordinate scaling for responsive design
 * - Polygon-based click detection for irregular button shapes
 * - Visual feedback with button outlines and overlays
 * - State-aware button coloring (normal/idle/active modes)
 * - Line counter display on controls panel
 * 
 * USAGE EXAMPLE:
 * 
 * // 1. Include the module in your HTML
 * <script src="controlsModule.js"></script>
 * 
 * // 2. Create controls instance
 * const controls = new ControlsModule(canvas, ctx, { width: 1920, height: 1020 });
 * 
 * // 3. Initialize the controls
 * controls.initialize();
 * 
 * // 4. Define button callbacks
 * const controlsCallbacks = {
 *     playback_mode: function() { console.log('Playback mode toggled'); },
 *     forward: function() { console.log('Forward/Play button pressed'); },
 *     pause: function() { console.log('Pause button pressed'); },
 *     // ... etc for all buttons
 * };
 * 
 * // 5. Handle clicks in your event handler
 * function handlePointerDown(pos) {
 *     if (controls.handleClick(pos, controlsCallbacks)) {
 *         return; // Controls handled the click
 *     }
 *     // Handle other clicks...
 * }
 * 
 * // 6. Draw controls in your render loop
 * function draw() {
 *     const state = {
 *         currentPoemLine: currentLine,
 *         playbackMode: "normal", // or "playback_idle", "playback_active"
 *         totalRecorderMode: false
 *     };
 *     controls.draw(state);
 * }
 * 
 * // 7. Update on window resize
 * window.addEventListener('resize', function() {
 *     controls.updateSize();
 * });
 * 
 * BUTTON NAMES:
 * - playback_mode: Toggles between normal/playback modes
 * - forward: Main play/pause button
 * - fast_rewind: Rewind/previous button  
 * - fast_forward: Fast forward/next button
 * - pause: Pause button
 * - stop_eject: Stop/restart button
 * - record: Record button
 */

class ControlsModule {
    constructor(canvas, ctx, screenDimensions) {
        this.canvas = canvas;
        this.ctx = ctx;
        this.SCREEN_WIDTH = screenDimensions.width;
        this.SCREEN_HEIGHT = screenDimensions.height;
        
        // Original controls image coordinates (2040 x 3708 pixels)
        this.ORIGINAL_CONTROLS_SIZE = { width: 2040, height: 3708 };
        
        // Button coordinates from original image
        this.buttonCoordsOriginal = {
            "playback_mode": [[200, 30], [1800, 30], [1800, 180], [200, 180]],
            "forward": [[63, 1953], [1866, 1851], [1888, 2048], [79, 2166]],
            "fast_rewind": [[162, 1242], [1011, 1207], [1038, 1411], [189, 1455]],
            "fast_forward": [[1216, 1216], [1987, 1194], [2010, 1393], [1251, 1413]],
            "pause": [[1170, 2632], [1944, 2563], [1966, 2766], [1197, 2844]],
            "stop_eject": [[154, 3454], [1934, 3229], [1956, 3434], [176, 3666]],
            "record": [[136, 2702], [976, 2619], [1002, 2844], [124, 2929]]
        };
        
        // Controls state
        this.controlsImage = null;
        this.controlsImageSize = { width: 0, height: 0 };
        this.controlsX = 20;
        this.controlsY = 0;
        this.controlsHeight = 0;
        this.controlsWidth = 0;
        this.scaledButtonCoords = {};
    }

    /**
     * Initialize the controls module
     */
    initialize() {
        this.calculateControlsSize();
        this.loadControlsImage();
    }

    /**
     * Calculate controls image display size
     */
    calculateControlsSize() {
        this.controlsHeight = Math.floor(this.SCREEN_HEIGHT / 3) + 72;
        this.controlsWidth = Math.floor(this.controlsHeight * (this.ORIGINAL_CONTROLS_SIZE.width / this.ORIGINAL_CONTROLS_SIZE.height));
        this.controlsY = this.SCREEN_HEIGHT - this.controlsHeight - 20;
        this.controlsImageSize = { width: this.controlsWidth, height: this.controlsHeight };
    }

    /**
     * Load controls image from file or create default
     */
    loadControlsImage() {
        this.controlsImage = new Image();
        this.controlsImage.onload = () => {
            console.log('Controls loaded');
            this.scaleButtonCoords();
        };
        this.controlsImage.onerror = () => {
            console.log('Controls failed to load, using default');
            this.createDefaultControls();
        };
        this.controlsImage.src = 'controls.jpg';
    }

    /**
     * Create default controls image when file loading fails
     */
    createDefaultControls() {
        this.calculateControlsSize();
        const controlsCanvas = document.createElement('canvas');
        controlsCanvas.width = this.controlsWidth;
        controlsCanvas.height = this.controlsHeight;
        const controlsCtx = controlsCanvas.getContext('2d');
        
        const controlsGradient = controlsCtx.createLinearGradient(0, 0, this.controlsWidth, this.controlsHeight);
        controlsGradient.addColorStop(0, '#8b4513');
        controlsGradient.addColorStop(0.5, '#654321');
        controlsGradient.addColorStop(1, '#4a2c2a');
        controlsCtx.fillStyle = controlsGradient;
        controlsCtx.fillRect(0, 0, this.controlsWidth, this.controlsHeight);
        
        controlsCtx.strokeStyle = '#3a1f1a';
        controlsCtx.lineWidth = 2;
        for (let y = 20; y < this.controlsHeight; y += 40) {
            controlsCtx.beginPath();
            controlsCtx.moveTo(0, y);
            controlsCtx.lineTo(this.controlsWidth, y);
            controlsCtx.stroke();
        }
        
        this.controlsImage = new Image();
        this.controlsImage.src = controlsCanvas.toDataURL();
        this.scaleButtonCoords();
    }

    /**
     * Scale button coordinates based on current controls image size
     */
    scaleButtonCoords() {
        this.scaledButtonCoords = {};
        if (this.controlsImage && this.controlsImageSize.width > 0) {
            for (const buttonName in this.buttonCoordsOriginal) {
                const coords = this.buttonCoordsOriginal[buttonName];
                const scaledCoords = this.scaleButtonCoordinates(coords, this.ORIGINAL_CONTROLS_SIZE, this.controlsImageSize);
                const finalCoords = this.offsetCoordinates(scaledCoords, this.controlsX, this.controlsY);
                this.scaledButtonCoords[buttonName] = finalCoords;
            }
        }
    }

    /**
     * Scale button coordinates from original image to scaled image
     */
    scaleButtonCoordinates(originalCoords, originalImageSize, scaledImageSize) {
        const scaleX = scaledImageSize.width / originalImageSize.width;
        const scaleY = scaledImageSize.height / originalImageSize.height;
        
        return originalCoords.map(function(coord) {
            return [
                Math.floor(coord[0] * scaleX),
                Math.floor(coord[1] * scaleY)
            ];
        });
    }

    /**
     * Add offset to all coordinates
     */
    offsetCoordinates(coords, offsetX, offsetY) {
        return coords.map(function(coord) {
            return [coord[0] + offsetX, coord[1] + offsetY];
        });
    }

    /**
     * Check if point is inside polygon using ray casting algorithm
     */
    pointInPolygon(point, polygon) {
        const x = point.x, y = point.y;
        let inside = false;
        
        for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
            const xi = polygon[i][0], yi = polygon[i][1];
            const xj = polygon[j][0], yj = polygon[j][1];
            
            if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) {
                inside = !inside;
            }
        }
        
        return inside;
    }

    /**
     * Check which button was clicked
     */
    checkButtonClick(pos, buttonCoords) {
        for (const buttonName in buttonCoords) {
            if (this.pointInPolygon(pos, buttonCoords[buttonName])) {
                return buttonName;
            }
        }
        return null;
    }

    /**
     * Draw button outline
     */
    drawButtonOutline(coords, color, width) {
        if (coords.length < 3) {
            return;
        }
        
        this.ctx.strokeStyle = this.rgbToString(color || [0, 255, 0]);
        this.ctx.lineWidth = width || 2;
        this.ctx.beginPath();
        this.ctx.moveTo(coords[0][0], coords[0][1]);
        for (let i = 1; i < coords.length; i++) {
            this.ctx.lineTo(coords[i][0], coords[i][1]);
        }
        this.ctx.closePath();
        this.ctx.stroke();
    }

    /**
     * Draw filled polygon
     */
    drawFilledPolygon(coords, color) {
        if (coords.length < 3) {
            return;
        }
        
        this.ctx.fillStyle = this.rgbToString(color);
        this.ctx.beginPath();
        this.ctx.moveTo(coords[0][0], coords[0][1]);
        for (let i = 1; i < coords.length; i++) {
            this.ctx.lineTo(coords[i][0], coords[i][1]);
        }
        this.ctx.closePath();
        this.ctx.fill();
    }

    /**
     * Convert RGB array to CSS color string
     */
    rgbToString(rgb) {
        return `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
    }

    /**
     * Update controls size (call on window resize)
     */
    updateSize() {
        this.calculateControlsSize();
        this.scaleButtonCoords();
    }

    /**
     * Handle controls click
     * @param {Object} pos - Position object with x and y coordinates
     * @param {Object} callbacks - Object containing callback functions for each button
     * @returns {boolean} - True if a button was clicked, false otherwise
     */
    handleClick(pos, callbacks) {
        if (Object.keys(this.scaledButtonCoords).length > 0) {
            const clickedButton = this.checkButtonClick(pos, this.scaledButtonCoords);
            if (clickedButton && callbacks[clickedButton]) {
                console.log(`Controls button clicked: ${clickedButton}`);
                callbacks[clickedButton]();
                return true;
            }
        }
        return false;
    }

    /**
     * Draw the controls image and button overlays
     * @param {Object} state - Application state object containing display information
     */
    draw(state) {
        if (this.controlsImage && this.controlsImage.complete) {
            this.ctx.drawImage(this.controlsImage, this.controlsX, this.controlsY, this.controlsWidth, this.controlsHeight);
            
            // Show current line number as 3-digit counter on controls
            if (state.currentPoemLine !== undefined) {
                const lineNumber = String(state.currentPoemLine).padStart(3, '0');
                this.ctx.fillStyle = 'rgb(0, 255, 0)';
                this.ctx.font = 'bold 24px "Courier New"';
                this.ctx.textAlign = 'left';
                this.ctx.textBaseline = 'top';
                this.ctx.fillText(lineNumber, this.controlsX + 50, this.controlsY + 20);
            }
            
            // Draw button outlines and overlays
            for (const buttonName in this.scaledButtonCoords) {
                const coords = this.scaledButtonCoords[buttonName];
                if (buttonName === "playback_mode") {
                    let color;
                    if (state.playbackMode === "normal") {
                        color = [0, 180, 0];
                    } else if (state.playbackMode === "playback_idle") {
                        color = [200, 200, 0];
                    } else {
                        color = [200, 0, 0];
                    }
                    
                    this.drawFilledPolygon(coords, color);
                    this.drawButtonOutline(coords, [101, 67, 33], 4);
                    
                } else {
                    let color;
                    let width = 3;
                    
                    if (buttonName === "forward") {
                        color = [0, 255, 0];
                    } else if (buttonName === "pause") {
                        color = [255, 255, 0];
                    } else if (buttonName === "stop_eject") {
                        color = [255, 0, 0];
                    } else if (buttonName === "fast_rewind") {
                        color = [0, 150, 255];
                    } else if (buttonName === "fast_forward") {
                        color = [0, 150, 255];
                    } else if (buttonName === "record") {
                        if (state.playbackMode !== "normal") {
                            color = [100, 100, 100];
                        } else {
                            color = state.totalRecorderMode ? [255, 50, 50] : [0, 255, 0];
                            width = state.totalRecorderMode ? 5 : 3;
                        }
                    } else {
                        color = [255, 255, 255];
                    }
                    
                    this.drawButtonOutline(coords, color, width);
                }
            }
        }
    }

    /**
     * Get controls dimensions and position
     */
    getDimensions() {
        return {
            x: this.controlsX,
            y: this.controlsY,
            width: this.controlsWidth,
            height: this.controlsHeight
        };
    }

    /**
     * Get scaled button coordinates
     */
    getButtonCoords() {
        return this.scaledButtonCoords;
    }

    /**
     * Check if controls image is loaded
     */
    isLoaded() {
        return this.controlsImage && this.controlsImage.complete;
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ControlsModule;
}