from PIL import Image, ImageDraw, ImageOps, ImageFont
import cv2


class ParkingLotDetection:
    def __init__(self):
        self.image_name = "Input Images/Parking Lot 5x3 (6).png"
        self.lot = []
        self.lot_coords = []
        self.image = Image.open(self.image_name)
        self.output_image = self.image.copy()
        self.numberOfLots = 0
        self.numberOfEmptyLots = 0
        self.numberOfOccupiedLots = 0
        self.ifEmpty = []
        self.wrongParked = []

    def checkIfEmpty(self, i):
        # Use image filling on each lot
        self.image_fill(i)
        lot_histogram = self.lot[i].histogram()  # Get the intensity histogram in form of list
        lot_sum = sum(lot_histogram)  # Finding sum of intensities
        # print("Total pixels - " + str(lot_sum) + "\tNumber of white pixels - " + str(lot_histogram[255]), end="")
        white_pixels = lot_histogram[255]
        if white_pixels > (lot_sum * 0.92):  # If white pixels are more than 92%
            print("\tLot is EMPTY")
            self.numberOfEmptyLots += 1
            self.ifEmpty.append(True)
        else:
            print("\tLot is OCCUPIED", end="")
            self.numberOfOccupiedLots += 1
            self.ifEmpty.append(False)
            if self.checkProperParking(i):
                print("\t\tProperly Parked")
            else:
                print("\t\tNot Properly Parked")
                self.wrongParked.append(i)

    def checkProperParking(self, i):
        lot_image = self.lot[i]
        width, length = lot_image.size
        # Top Layer
        for x in range(width):
            for y in range(int(length * 0.02)):
                if lot_image.getpixel((x, y)) != 255:
                    return False
        # Bottom Layer
        for x in range(width):
            for y in range(int(length * 0.98), length):
                if lot_image.getpixel((x, y)) != 255:
                    return False
        # Left Layer
        for x in range(int(width * 0.02)):
            for y in range(length):
                if lot_image.getpixel((x, y)) != 255:
                    return False
        # Right Layer
        for x in range(int(width * 0.98), width):
            for y in range(length):
                if lot_image.getpixel((x, y)) != 255:
                    return False
        # Return true if Properly parked
        return True

    def image_fill(self, i):
        # Make copy of image
        mask = self.lot[i].copy()
        # Flooding the image background
        ImageDraw.floodfill(mask, (0, 0), 0)
        # Invert the image
        mask = ImageOps.invert(mask)
        # mask.save("lots/mask " + str(i + 1) + ".png")
        # Applying the mask to the lot image
        filled_image = self.mask_image(self.lot[i], mask)
        filled_image.save("lots/lot " + str(i + 1) + ".png")

    def mask_image(self, img, mask):
        width, length = img.size
        filled_img = img
        # If pixels are same make it white, else black
        for x in range(0, width):
            for y in range(0, length):
                if mask.getpixel((x, y)) == img.getpixel((x, y)):
                    filled_img.putpixel((x, y), 255)
                else:
                    filled_img.putpixel((x, y), 0)
        return filled_img

    def getLots(self):
        im = cv2.imread(self.image_name)
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        ret, gray = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2:]
        for cnt in contours:
            # Finding Coordinates and width, height of each contour
            x, y, w, h = cv2.boundingRect(cnt)
            if w == 350 and h == 630:
                # Extracting Region of Interest
                roi = im[y:y + h, x:x + w]
                # Adding Lot and it's coordinates in the list
                self.numberOfLots += 1
                self.lot_coords.append([x, y])
                self.lot.append(Image.fromarray(roi))
                self.lot[self.numberOfLots - 1] = self.lot[self.numberOfLots - 1].convert("L")

    def saveLots(self):
        # Saving the image in a folder
        for i in range(0, self.numberOfLots):
            self.lot[i].save("lots/Lot " + str(i + 1) + ".png")

    def thresholding(self, lot_image):
        width, length = lot_image.size
        # Thresholding value : 200
        for x in range(0, width):
            for y in range(0, length):
                if lot_image.getpixel((x, y)) > 200:
                    lot_image.putpixel((x, y), 255)
                else:
                    lot_image.putpixel((x, y), 0)
        return lot_image

    def addBorder(self, coords, img, text_font, text):
        # Used for adding border to text
        black = (0, 0, 0)
        x, y = coords
        img.text((x - 2, y), text, black, font=text_font)
        img.text((x, y - 2), text, black, font=text_font)
        img.text((x + 2, y), text, black, font=text_font)
        img.text((x, y + 2), text, black, font=text_font)

    def putStatus(self):
        # Creating text, image and colour variables
        text_font = ImageFont.truetype("arial.ttf", 60)
        self.image = Image.open(self.image_name)
        red = (255, 0, 0)
        green = (0, 255, 0)
        white = (255, 255, 255)
        img = ImageDraw.Draw(self.image)
        # Checking from list if empty and printing the appropriate status
        for i in range(self.numberOfLots):
            if self.ifEmpty[i]:
                self.addBorder((self.lot_coords[i][0], self.lot_coords[i][1] + 315), img, text_font, "    EMPTY")
                img.text((self.lot_coords[i][0], self.lot_coords[i][1] + 315), "    EMPTY", white, font=text_font)
            else:
                self.addBorder((self.lot_coords[i][0], self.lot_coords[i][1] + 315), img, text_font, " OCCUPIED")
                if i in self.wrongParked:
                    img.text((self.lot_coords[i][0], self.lot_coords[i][1] + 315), " OCCUPIED", red, font=text_font)
                else:
                    img.text((self.lot_coords[i][0], self.lot_coords[i][1] + 315), " OCCUPIED", green, font=text_font)
        # Displaying the image and saving it
        self.image.show()
        self.image.save("output/Output.png")

    def output(self):
        print("\n----------------------------------------------------------------")
        print("Number of Lots : " + str(self.numberOfLots))
        print("Number of Empty Lots : " + str(self.numberOfEmptyLots))
        print("Number of Occupied Lots : " + str(self.numberOfOccupiedLots))

    def run(self):
        # Converting image to grayscale
        self.image = self.image.convert("L")
        self.getLots()
        # Reversing the order of list
        self.lot.reverse()
        self.lot_coords.reverse()
        # Thresholding each lot image
        print("Thresholding Image...........", end="")
        for i in range(self.numberOfLots):
            self.lot[i] = self.thresholding(self.lot[i])
        print("DONE")
        # Saving lots in files
        self.saveLots()
        # Check for each Lot if it is empty
        print("Examining Lots.......")
        for i in range(self.numberOfLots):
            print("Lot " + str(i + 1) + " - ", end="")
            self.checkIfEmpty(i)
        # Output
        self.output()
        self.putStatus()


obj = ParkingLotDetection()
obj.run()
