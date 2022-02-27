import math
import json
import random


from PyQt5.QtCore import (QLineF, QPointF, QRectF, QSizeF, qsrand,
                          Qt, QTime, QUuid)

from PyQt5.QtCore import (QSortFilterProxyModel, Qt,
                          QTime, pyqtSignal)

from PyQt5.QtGui import (QBrush, QColor, QPainter,
                         QPainterPath, QPen, QRadialGradient, QIcon, QStandardItemModel, QStandardItem, QMouseEvent)

from PyQt5.QtWidgets import *

from ImAnaliz.DetectionTEXT_N_OBJS import initAnalyse


class Edge(QGraphicsItem):
    Pi = math.pi
    TwoPi = 2.0 * Pi

    Type = QGraphicsItem.UserType + 2

    def __init__(self, sourceNode, destNode):
        super(Edge, self).__init__()

        self.arrowSize = 10.0
        self.sourcePoint = QPointF()
        self.destPoint = QPointF()

        self.setAcceptedMouseButtons(Qt.NoButton)
        self.source = sourceNode
        self.dest = destNode
        self.source.addEdge(self)
        self.dest.addEdge(self)
        self.adjust()

    def type(self):
        return Edge.Type

    def sourceNode(self):
        return self.source

    def setSourceNode(self, node):
        self.source = node
        self.adjust()

    def destNode(self):
        return self.dest

    def setDestNode(self, node):
        self.dest = node
        self.adjust()

    def adjust(self):
        if not self.source or not self.dest:
            return

        line = QLineF(self.mapFromItem(self.source, 0, 0),
                      self.mapFromItem(self.dest, 0, 0))
        length = line.length()

        self.prepareGeometryChange()

        if length > 20.0:
            edgeOffset = QPointF((line.dx() * 10) / length,
                                 (line.dy() * 10) / length)

            self.sourcePoint = line.p1() + edgeOffset
            self.destPoint = line.p2() - edgeOffset
        else:
            self.sourcePoint = line.p1()
            self.destPoint = line.p1()

    def boundingRect(self):
        if not self.source or not self.dest:
            return QRectF()

        penWidth = 1.0
        extra = (penWidth + self.arrowSize) / 2.0

        return QRectF(self.sourcePoint,
                      QSizeF(self.destPoint.x() - self.sourcePoint.x(),
                             self.destPoint.y() - self.sourcePoint.y())).normalized().adjusted(-extra, -extra, extra,
                                                                                               extra)

    def paint(self, painter, option, widget):
        if not self.source or not self.dest:
            return

        # Draw the line itself.
        line = QLineF(self.sourcePoint, self.destPoint)

        if line.length() == 0.0:
            return

        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap,
                            Qt.RoundJoin))
        painter.drawLine(line)


class Node(QGraphicsItem):
    Type = QGraphicsItem.UserType + 1

    def __init__(self, graphWidget):
        super(Node, self).__init__()
        self.uuid = str(random.randint(1, 100)) + str(random.randint(1, 100))
        self.graph = graphWidget
        self.edgeList = []
        self.newPos = QPointF()

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setZValue(1)

    def type(self):
        return Node.Type

    def addEdge(self, edge):
        self.edgeList.append(edge)
        edge.adjust()

    def edges(self):
        return self.edgeList

    def calculatePosition(self):
        if not self.scene() or self.scene().mouseGrabberItem() is self:
            self.newPos = self.pos()
            return

        xvel = 0.0
        yvel = 0.0

        sceneRect = self.scene().sceneRect()
        self.newPos = self.pos() + QPointF(xvel, yvel)
        self.newPos.setX(min(max(self.newPos.x(), sceneRect.left() + 20), sceneRect.right() - 10))
        self.newPos.setY(min(max(self.newPos.y(), sceneRect.top() + 20), sceneRect.bottom() - 10))

    def advance(self):
        if self.newPos == self.pos():
            return False

        self.setPos(self.newPos)
        return True

    def boundingRect(self):
        adjust = 2.0
        return QRectF(-10 - adjust, -10 - adjust, 23 + adjust, 23 + adjust)

    def shape(self):
        path = QPainterPath()
        path.addEllipse(-10, -10, 20, 20)
        return path

    def paint(self, painter, option, widget):
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.darkGray)
        painter.drawEllipse(-7, -7, 20, 20)

        gradient = QRadialGradient(-3, -3, 10)
        if option.state & QStyle.State_Sunken:
            gradient.setCenter(3, 3)
            gradient.setFocalPoint(3, 3)
            gradient.setColorAt(1, QColor(Qt.yellow).lighter(120))
            gradient.setColorAt(0, QColor(Qt.darkYellow).lighter(120))
        else:
            gradient.setColorAt(0, Qt.yellow)
            gradient.setColorAt(1, Qt.darkYellow)

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(Qt.black, 0))
        painter.drawEllipse(-10, -10, 20, 20)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edgeList:
                edge.adjust()
            self.graph.itemMoved()

        return super(Node, self).itemChange(change, value)

    def mousePressEvent(self, event):
        self.update()
        super(Node, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.update()
        super(Node, self).mouseReleaseEvent(event)


class Rectangle(Node):
    # Square

    def paint(self, painter, option, widget):
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.darkGray)
        painter.drawRect(-7, -7, 20, 20)

        gradient = QRadialGradient(-3, -3, 10)
        if option.state & QStyle.State_Sunken:
            gradient.setCenter(3, 3)
            gradient.setFocalPoint(3, 3)
            gradient.setColorAt(1, QColor(Qt.yellow).lighter(120))
            gradient.setColorAt(0, QColor(Qt.darkYellow).lighter(120))
        else:
            gradient.setColorAt(0, Qt.yellow)
            gradient.setColorAt(1, Qt.darkYellow)

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(Qt.black, 0))
        painter.drawRect(-10, -10, 20, 20)


class Triangle(Node):
    # Triangle

    def paint(self, painter, option, widget):
        rect = QRectF(-7, -7, 20, 20)

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.darkGray)

        third = QPointF(int(rect.left() + (rect.width() / 2)), int(rect.top()))
        painter.drawPolygon(rect.bottomLeft(), rect.bottomRight(), third)
        gradient = QRadialGradient(-3, -3, 10)

        if option.state & QStyle.State_Sunken:
            gradient.setCenter(3, 3)
            gradient.setFocalPoint(3, 3)
            gradient.setColorAt(1, QColor(Qt.yellow).lighter(120))
            gradient.setColorAt(0, QColor(Qt.darkYellow).lighter(120))
        else:
            gradient.setColorAt(0, Qt.yellow)
            gradient.setColorAt(1, Qt.darkYellow)

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(Qt.black, 0))
        rect = QRectF(-7, -7, 20, 20)

        third = QPointF(int(rect.left() + (rect.width() / 2)), int(rect.top()))
        painter.drawPolygon(rect.bottomLeft(), rect.bottomRight(), third)


class TextItem(QGraphicsTextItem):
    lostFocus = pyqtSignal(QGraphicsTextItem)

    selectedChange = pyqtSignal(QGraphicsItem)

    def __init__(self, parent=None, scene=None):
        super(TextItem, self).__init__(parent, scene)

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            self.selectedChange.emit(self)
        return value

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.lostFocus.emit(self)
        super(TextItem, self).focusOutEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.textInteractionFlags() == Qt.NoTextInteraction:
            self.setTextInteractionFlags(Qt.TextEditorInteraction)
        super(TextItem, self).mouseDoubleClickEvent(event)


class GraphWidget(QGraphicsView):
    def __init__(self, ui):
        super(GraphWidget, self).__init__()

        self.timerId = 0

        self.scene = QGraphicsScene(self)
        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.scene.setSceneRect(0, 0, 800, 800)
        self.setScene(self.scene)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)


        self.scale(0.8, 0.8)

    def itemMoved(self):
        if not self.timerId:
            self.timerId = self.startTimer(1000)

    def timerEvent(self, event):
        nodes = [item for item in self.scene.items() if isinstance(item, Node) or isinstance(item, Triangle) or isinstance(item, Rectangle)]

        for node in nodes:
            node.calculatePosition()

        itemsMoved = False
        for node in nodes:
            if node.advance():
                itemsMoved = True

        if not itemsMoved:
            self.killTimer(self.timerId)
            self.timerId = 0

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.angleDelta().y() / 240.0))

    def drawBackground(self, painter, rect):
        sceneRect = self.sceneRect()

        # Fill.
        brush = QBrush(Qt.lightGray)
        painter.fillRect(rect.intersected(sceneRect), brush)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(sceneRect)

        # # Text.
        # textRect = QRectF(sceneRect.left() + 4, sceneRect.top() + 4,
        #                   sceneRect.width() - 4, sceneRect.height() - 4)
        # message = "Вы можете передвигать графические примитивы!"
        #
        # font = painter.font()
        # font.setBold(True)
        # font.setPointSize(14)
        # painter.setFont(font)
        # painter.setPen(Qt.black)

    def scaleView(self, scaleFactor):
        factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()

        if factor < 0.07 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)


class ItemMaker:
    @staticmethod
    def makeTriangleItem(ui, graphWidget, name, form, x, y, item):
        ui.addData(name, form, item.uuid)
        graphWidget.scene.addItem(item)
        item.setPos(x, y)

    @staticmethod
    def makeCircleItem(ui, graphWidget, name, form, x, y, item):
        ui.addData(name, form,  item.uuid)
        graphWidget.scene.addItem(item)
        item.setPos(x, y)

    @staticmethod
    def makeRectangleItem(ui, graphWidget, name, form, x, y, item):
        ui.addData(name, form,  item.uuid)
        graphWidget.scene.addItem(item)
        item.setPos(x, y)

    @staticmethod
    def makeTextItem(graphWidget, x, y, item):
        graphWidget.scene.addItem(item)
        item.setPos(x, y)


class EdgeMaker:
    @staticmethod
    def makeEdge(graphWidget, firstItem, secondItem):
        graphWidget.scene.addItem(Edge(firstItem, secondItem))


class GenerateScene:
    def __init__(self, ui, graphWidget):
        self.ui = ui
        self.graphWidget = graphWidget

    @staticmethod
    def openFile(path):
        with open(path) as json_file:
            data = json.load(json_file)
        return data

    def sceneByItems(self, path):
        data = GenerateScene.openFile(path)

        for form, coordinates, text in data.values():
            x, y = coordinates
            x /= 4
            y /= 4
            if "Triangle" == form:
                triangle = Triangle(self.graphWidget)
                ItemMaker.makeTriangleItem(self.ui, self.graphWidget, "trash", form, x, y, triangle)
            if "Circle" == form:
                circle = Node(self.graphWidget)
                ItemMaker.makeCircleItem(self.ui, self.graphWidget, "trash", form, x, y, circle)
            if "Rectangle" == form:
                rectangle = Rectangle(self.graphWidget)
                ItemMaker.makeRectangleItem(self.ui, self.graphWidget, "trash", form, x, y, rectangle)
            textItem = TextItem(text)
            ItemMaker.makeTextItem(self.graphWidget, x, y - 30, textItem)

class Ui(QWidget):
    """

    :param QWidgets:
    :return:
    """

    def __init__(self):
        super().__init__()

        self.filePath = None

        self.initUi()

    def initUi(self):
        self.move(300, 300)
        self.setWindowTitle('AeroSpacePro 2022')
        self.setWindowIcon(QIcon('icon.jpg'))
        mainLayout = QVBoxLayout()

        self.dataView = QTreeView()
        self.dataView.doubleClicked.connect(self.treeItemDoubleClicked)
        self.dataView.setSortingEnabled(True)
        self.dataView.setRootIsDecorated(False)
        self.dataView.setAlternatingRowColors(True)
        self.model = self.createModel(self.dataView)
        self.dataView.setModel(self.model)
        self.sceneGraphWidget = GraphWidget(self)

        self.loadBtn = QPushButton(self)
        self.loadBtn.setText("Открыть изображение")
        self.loadBtn.clicked.connect(self.loadFromImage)

        mainLayout.addWidget(self.dataView)
        mainLayout.addWidget(self.sceneGraphWidget)
        mainLayout.addWidget(self.loadBtn)
        self.setLayout(mainLayout)
        self.setMinimumSize(300, 300)
        self.resize(600, 600)
        self.show()

    def treeItemDoubleClicked(self, index):
        """

        :return:
        """
        items = self.sceneGraphWidget.scene.items()
        keyToFind = index.model().itemFromIndex(index).data(1)
        print(items)
        for item in items:
            print(str(item.uuid) + " : " + str(keyToFind))
            if keyToFind == item.uuid:
                print("hello")

    def createModel(self, parent):
        model = QStandardItemModel(0, 2, parent)
        model.setHeaderData(0, Qt.Horizontal, "Форма")
        model.setHeaderData(1, Qt.Horizontal, "Текстовая надпись")
        return model

    def addData(self, name, form,  uuid):
        self.model.insertRow(0)

        item = QStandardItem()
        item.setEditable(False)
        item.setData(uuid, 1)
        item.setText(name)
        self.model.setItem(0, 0, item)

        item = QStandardItem()
        item.setEditable(False)
        item.setData(uuid, 1)
        item.setText(form)
        self.model.setItem(0, 1, item)

    def loadFromImage(self):
        self.filePath, _ = QFileDialog.getOpenFileName(self,
                                                       'Открыть изображение',
                                                       './',
                                                       'Image (*.jpg)')
        if self.filePath is not None and self.filePath:
            # тут заюзать конверт
            jsonPath = Convert.convertFromImageToJson(self.filePath)
            generator = GenerateScene(ui, self.sceneGraphWidget)
            generator.sceneByItems(jsonPath)

class Convert:
    """
    Класс для связи изображений и сцены
    """
    @staticmethod
    def convertFromImageToJson(imagePath):
        return initAnalyse(imagePath)

    @staticmethod
    def convertFromJsonToModel(jsonPath):
        pass

    @staticmethod
    def convertFromImageToModel(imagePath):
        pass


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    qsrand(QTime(0, 0, 0).secsTo(QTime.currentTime()))

    ui = Ui()
    ui.initUi()

    sys.exit(app.exec_())
