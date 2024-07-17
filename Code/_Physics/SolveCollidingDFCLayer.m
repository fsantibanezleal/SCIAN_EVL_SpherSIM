function layerDFC = SolveCollidingDFCLayer(enviroment)
% Basic copy
    layerDFC = enviroment.layerDFC;

%% Update colliding DFCs vertexs by iterative correction
    numDFCs = size(layerDFC.cellDFC,2);
    for indexDFC1 = 1:(numDFCs-1)
        for indexDFC2 = (indexDFC1+1):numDFCs
            %% dummy Versions of cells
            dummyDFC1 = layerDFC.cellDFC(indexDFC1);
            dummyDFC2 = layerDFC.cellDFC(indexDFC2);
            %% Estimate distance between DFCs
            distance = (dummyDFC1.center.AER(1)-...
                            dummyDFC2.center.AER(1)).^2 +...
                       (dummyDFC1.center.AER(2)-...
                            dummyDFC2.center.AER(2)).^2;
            
            bNearest = distance < ...
                        (dummyDFC1.radialSize + dummyDFC2.radialSize).^2;
            %% Only process cell in collision distance
            if bNearest
                [dummyDFC1,dummyDFC2] =...
                      SolveCollision_DFC2DFC(dummyDFC1,dummyDFC2);
                layerDFC.cellDFC(indexDFC1) = dummyDFC1;
                layerDFC.cellDFC(indexDFC2) = dummyDFC2;
            end
        end
    end    

end

